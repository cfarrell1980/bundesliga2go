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

class InvocationError(Exception):
  '''If openligadb.de is given the wrong parameters for a particular query
     or if it has no data for the query then a SOAP error occurs. Handle this!
  '''
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)


class BundesligaAPI:

  def __init__(self):
    self.oldb = OpenLigaDB()

  def getUpdates(self,tstamp,league,season):
    '''The client is sent a timestamp with each response. When the client makes the
       next request the client sends the same timestamp back to the server, which
       checks if any data need be returned to the client. This function queries the
       middleware database with the client's timestamp to obtain matchdata that 
       arrived since the client's timestamp. Only such updates are sent back to the
       client
    '''
    #TODO: it is possible that something will change in the Match object - e.g. the Match
    #field isFinished will change from False to True. This is currently not taken care of
    #by the getUpdates method, even though it would be relatively trivial given that the
    #Match object is already readily available at the time the goals are returned
    if not isinstance(tstamp,datetime):
      raise TypeError, "tstamp must be a datetime.datetime type!"
    session = Session()
    updates = session.query(Match).join(Goal).join(Matchday).join(League).filter(League.year==season).filter(Match.isFinished==True).filter(Match.startTime >= tstamp).all()
    goals = {}
    goalindex = {}
    for match in updates:
      for g in match.goals:
       goals[g.id] = {'scorer':g.scorer.encode('utf-8'),'minute':g.minute,'penalty':g.penalty,'ownGoal':g.ownGoal,'teamID':g.for_team_id}
       goalindex[g.match.id] = [x.id for x in g.match.goals]
    rd = (goals,goalindex)
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
    if not last_match_change or not last_matchday_change or not last_goal_change:
      print "No local data available for %s %d. Performing update..."%(league,season)
      update_required = True
    elif last_match_change.mtime < remote_tstamp or last_matchday_change.mtime < remote_tstamp or last_goal_change.mtime < remote_tstamp:
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
                    gdata = session.merge(Goal(g.goalID,g.goalGetterName.encode('utf-8'),g.goalMatchMinute,
                                    g.goalScoreTeam1,g.goalScoreTeam2,g.goalOwnGoal,g.goalPenalty))
                    match.goals.append(gdata)
          for goal in match.goals:# now try to find out what team scored. not easy from raw openligadb data
            if match.goals.index(goal) == 0:#the first goal is easy
              if match.goals[0].t1score == 1:
                match.goals[0].for_team_id = match.teams[0].id
              else:
                match.goals[0].for_team_id = match.teams[1].id
            else:#look to the last goal to see whose score increased
              prev1 = match.goals[match.goals.index(goal)-1].t1score
              prev2 = match.goals[match.goals.index(goal)-1].t2score
              if match.goals[match.goals.index(goal)].t1score > prev1:
                match.goals[match.goals.index(goal)].for_team_id = match.teams[0].id
              else:
                match.goals[match.goals.index(goal)].for_team_id = match.teams[1].id
              
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
    local_league = session.query(League).filter(League.year==season).filter_by(shortname=league).first()
    if not local_league:
      local_league = League(None,league,season)
    teams = local_league.teams
    if len(teams) < 18:# some seasons have strange 'teams' like 6. Platz Bundesliga
      print "Number of teams in %s for season %d is %d: UPDATING"%(league,season,len(teams))
      try:
        remote_teams = self.oldb.GetTeamsByLeagueSaison(league,season)
      except WebFault,e:
        raise InvocationError, "SOAP client could not complete request. Check parameters!"
      else:
        for t in remote_teams.Team:
          if not t.teamIconURL and t.teamID > 250:
            print "Ignoring %s as it doesn't seem to be a real team"%(t.teamName.encode('utf-8'))
          else:
            shortcut = None
            if t.teamID in shortcuts:
              shortcut = shortcuts[t.teamID]
            team = session.merge(Team(t.teamID,t.teamName.encode('utf-8'),t.teamIconURL,shortcut))
            team.leagues.append(local_league)
          session.commit()
      teams = local_league.teams
    else:
      print "Checking if any of the existing teams is missing a shortcut"
      for t in teams:
        if not t.shortcut:
          print "Yep...%s is missing a shortcut... checking if it has since been added..."%t.name.encode('utf-8')
          if shortcuts.has_key(t.id):
            print "Yep... seems to be in shortcuts as %s"%shortcuts[t.id]
            t.shortcut = shortcuts[t.id]
          else:
            print "No... you should add a shortcut for team %s (teamID %d) to bundesligaHelpers::shortcuts"%(t.name.encode('utf-8'),t.id)
        else:
          print "Yep...%d has shortcut %s...checking if it is still ok..."%(t.id,t.shortcut)
          if t.shortcut != shortcuts[t.id]:
            print "No...%s is the new shortcut...updating..."%shortcuts[t.id]
            t.shortcut = shortcuts[t.id]
      session.commit()
      print "There are 18 teams. Everything ok..."
    finish = time.time()
    print "<Running method getTeams() took %f seconds>"%(finish-start)
    return teams
          
