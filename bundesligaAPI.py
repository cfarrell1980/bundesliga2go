# -*- coding: utf-8 -*-
from OpenLigaDB import OpenLigaDB
from sqlalchemy.exc import IntegrityError
from bundesligaORM import *
from bundesligaHelpers import shortcuts,tstamp_to_md5
from suds import WebFault
import time
from datetime import datetime,timedelta

class AlreadyUpToDate(Exception):
  '''If the client's dataset is already up to date then raise this exception
     to tell the invoking script that it is ok to return an empty dataset
  '''
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)

class BundesligaAPI:

  def __init__(self):
    self.oldb = OpenLigaDB()

  def getUpdates(self,tstamp):
    '''The client stores certain timestamps. This method accepts
       the client's tstamp and the request the client has sent. The request is used
       to check which database tables are affected by the response. If the time stamp
       that the client sends is newer or equal to the most recent modification of any
       of the tables that is required to produce the data that the client requests then
       the client's localStorage dataset is already up to date and no data is returned
       to the client. Otherwise, the client's cache needs to be updated.
    '''
    if not isinstance(tstamp,datetime):
      raise TypeError, "tstamp must be a datetime.datetime type!"
    session = Session()
    updates = session.query(Goal).filter(Goal.mtime > tstamp).all()
    goals = {}
    goalindex = {}
    for g in updates:
      goals[g.id] = {'scorer':g.scorer.encode('utf-8'),'minute':g.minute,'penalty':g.penalty}
      goalindex[g.match.id] = [x.id for x in g.match.goals]
    rd = {'goalobjects':goals,'goalindex':goalindex}
    return rd

  def getMatchdataByLeagueSeason(self,league,season,client_tstamp=None):
    '''Return a dictionary holding data for matches returned for an entire
       season where the keys of the dictionary are the matchdays. The values
       are dictionaries containing the matchdata. If the client's tstamp is
       specified we additionally check if we can return an empty dataset - i.e
       if the client's tstamp indicates that the client's dataset is already
       up to date, then to save bandwidth we return an empty set
    '''
    if not isinstance(client_tstamp,datetime):
      print "client_tstamp %s is not a datetime object...ignoring"%client_tstamp
      client_tstamp = None
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
          if m.NumberOfViewers:
            viewers = m.NumberOfViewers
          else:
            viewers = 0
          match = session.merge(Match(m.matchID,m.matchDateTime,
                                  endTime,m.matchIsFinished,m.pointsTeam1,m.pointsTeam2,viewers))
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
          if m.goals:
            for aog in m.goals:
              for gobj in aog:
                if isinstance(gobj,list):
                  for g in gobj:
                   if hasattr(g,'goalGetterName'):
                    gdata = session.merge(Goal(g.goalID,g.goalGetterName.encode('utf-8'),g.goalMatchMinute,g.goalPenalty))
                    match.goals.append(gdata)
          md.matches.append(match)
      print "committing session..."
      session.commit()
      print "done...now returning the data..."
      local_matchdata = session.query(League).filter(League.year=='%d'%season).filter(League.shortname=='%s'%league).one()
    else:
      if client_tstamp:
        if client_tstamp > last_match_change.mtime and client_tstamp > last_matchday_change.mtime:# and client_tstamp > last_goal_change.mtime:
          print "Client tstamp: %s Match tstamp: %s Matchday tstamp: %s"%(client_tstamp,last_match_change.mtime,last_matchday_change.mtime)
          raise AlreadyUpToDate, "Client's timestamp indicates that client dataset is up to date"
        else: # no client tstamp was sent - this is fine, but we have to return all data
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
    update_required = False
    session = Session()
    remote_tstamp = self.oldb.GetLastChangeDateByGroupLeagueSaison(matchday,league,season)
    local_tstamp = session.query(Matchday.mtime).order_by(Matchday.mtime.desc()).first()
    if not local_tstamp:
      print "No local data available. Update required..."
      update_required = True
    else:
      if local_tstamp.mtime < remote_tstamp:
        print "Local data available but out of date. Update required..."
        update_required = True
      else:
        print "Local data available is up to date. No update required..."
    if update_required:
      remote_data = self.oldb.GetMatchdataByGroupLeagueSaison(matchday,league,season)
      print remote_data
    else:
      local_data = session.query(Matchday).filter(Matchday.matchdayNum==matchday).all()
    

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
    local_league = session.query(League).filter_by(shortname=league).first()
    if not local_league:
      local_league = League(None,league,season)
    teams = local_league.teams
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
          
