# -*- coding: utf-8 -*-
from OpenLigaDB import OpenLigaDB
from sqlalchemy.exc import IntegrityError
from bundesligaORM import *
from bundesligaHelpers import shortcuts
from suds import WebFault
import time
from datetime import datetime,timedelta

class BundesligaAPI:

  def __init__(self):
    self.oldb = OpenLigaDB()

  def getMatchdataByLeagueSeason(self,league,season):
    '''Return a dictionary holding data for matches returned for an entire
       season where the keys of the dictionary are the matchdays. The values
       are dictionaries containing the matchdata
    '''
    session=Session()
    update_required = False
    remote_tstamp = self.oldb.GetLastChangeDateByLeagueSaison(league,season)
    last_match_change = session.query(Match.mtime).order_by(Match.mtime.desc()).first()
    last_matchday_change = session.query(Matchday.mtime).order_by(Matchday.mtime.desc()).first()
    last_goal_change = session.query(Goal.mtime).order_by(Goal.mtime.desc()).first()
    if not last_match_change or not last_matchday_change:# or not last_goal_change:
      print "No local data available for %s %d. Performing update..."%(league,season)
      update_required = True
    elif last_match_change.mtime < remote_tstamp or last_matchday_change.mtime < remote_tstamp:# or last_goal_change < remote_tstamp:
      print "Local data appears to be outdated. Performing update of %s %d"%(league,season)
      update_required = True
    else:
      print "Local data for %s %d appears to be up to date"%(league,season)
    if update_required:
      local_league = session.query(League).filter_by(shortname=league).first()
      if not local_league:
        local_league = League(None,league,season)
      remote_matchdata = self.oldb.GetMatchdataByLeagueSaison(league,season)
      
      for m in remote_matchdata.Matchdata:
          md = session.query(Matchday).filter_by(matchdayNum='%d'%m.groupOrderID).first()
          if not md:
            md = Matchday(m.groupOrderID,m.groupName.encode('utf-8'))
            session.add(md)
          local_league.matchdays.append(md)
          # realistic default = 45+3+15+45+3?
          d = timedelta(minutes=111)
          endTime = m.matchDateTime+d
          match = session.merge(Match(m.matchID,m.matchDateTime,endTime,m.matchIsFinished))
          if m.idTeam1 in shortcuts.keys():
            shortcut1 = shortcuts[m.idTeam1]
          else:
            shortcut1 = None
          if m.idTeam2 in shortcuts.keys():
            shortcut2 = shortcuts[m.idTeam2]
          else:
            shortcut2 = None
          t1 = session.merge(Team(m.idTeam1,m.nameTeam1.encode('utf-8'),m.iconUrlTeam1,shortcut1))
          t2 = session.merge(Team(m.idTeam2,m.nameTeam2.encode('utf-8'),m.iconUrlTeam2,shortcut2))
          match.teams.append(t1)
          match.teams.append(t2)
          if t1 not in local_league.teams:
            local_league.teams.append(t1)
          if t2 not in local_league.teams:
            local_league.teams.append(t2)
          md.matches.append(match)
      print "committing session..."
      session.commit()
      print "done...now returning the data..."
      local_matchdata = session.query(League).filter(League.year=='%d'%season).filter(League.shortname=='%s'%league).one()
    else:
      local_matchdata = session.query(League).filter(League.year=='%d'%season).filter(League.shortname=='%s'%league).one()
    return local_matchdata

  def getMatchdataByLeagueSeasonMatchday(self,league,season,matchday):
    '''Return a dictionary holding data for the matchday for the given
       season and league. The keys of the dictionary are the matchIDs
       of the matches taking place. Thus, there should be 9 keys in any
       dictionary returned from this method
    '''
    session = Session()
    remote_tstamp = self.oldb.GetLastChangeDateByGroupLeagueSaison(matchday,league,season)
    q1 = session.query(Matchday.mtime).order_by(Matchday.mtime.desc()).first()
    print q1

  def getMatchdataByMatchID(self,matchID):
    pass

  def getGoalsByMatchID(self,matchID):
    pass

  def getTeams(self,league,season):
    '''Return a dictionary holding data for the teams in a given 
       season and league. The keys of the dictionary are the teamIDs.
    '''
    start = time.time()
    session=Session()
    #local_league = session.merge(League(None,league,season))
    local_league = session.query(League).filter_by(shortname=league).first()
    if not local_league:
      local_league = League(None,league,season)
    teams = local_league.teams
    print teams
    print type(teams)
    print len(teams) 
    if len(teams) != 18:
      print "Number of teams in %s for season %d is %d: UPDATING"%(league,season,len(teams))
      try:
        remote_teams = self.oldb.GetTeamsByLeagueSaison(league,season)
      except WebFault,e:
        raise StandardError, "SOAP client could not complete request. Check parameters!"
      else:
        for t in remote_teams.Team:
          shortcut = None
          if t.teamID in shortcuts:
            shortcut = shortcuts[t.teamID]
          team = session.merge(Team(t.teamID,t.teamName.encode('utf-8'),t.teamIconURL,shortcut))
          team.leagues.append(local_league)
        session.commit()
    else:
      print "There are 18 teams. Everything ok..."
    finish = time.time()
    print "<Running method getTeams() took %f seconds>"%(finish-start)
    return teams
          
