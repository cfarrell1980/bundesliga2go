# -*- coding: utf-8 -*-
from OpenLigaDB import OpenLigaDB
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_,or_,not_
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

  def getUpdates(self,tstamp,league,season,matchday=None):
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
    if not league:
      league = DEFAULT_LEAGUE
    if not season:
      season = current_bundesliga_season()
    if not self.localCacheValid(league,season):
      print "Local cache is not valid. Need to run getData(%s,%d)"%(league,season)
      try:
        d = self.setupLocal(league,season)
      except Exception,e:
        print e
      else:
        print "Retrieved data"
    session = Session()
    if not matchday:
      updates = session.query(Match).join(League).filter(and_(League.season==season,League.name==league,
                or_(Match.startTime > tstamp,and_(Match.startTime < tstamp,Match.endTime > tstamp)))).all()
    else:
      updates = session.query(Match).join(League).filter(and_(League.season==season,League.name==league,Match.matchday==matchday,
                or_(Match.startTime > tstamp,and_(Match.startTime < tstamp,Match.endTime > tstamp)))).all()
    goals = {}
    goalindex = {}
    for match in updates:
      for g in match.goals:
       goals[g.id] = {'scorer':g.scorer.encode('utf-8'),'minute':g.minute,'penalty':g.penalty,'ownGoal':g.ownGoal,'teamID':g.for_team_id}
       goalindex[g.match.id] = [x.id for x in g.match.goals]
    rd = (goals,goalindex)
    return rd

  def setupLocal(self,league,season):
    '''If there is no local data available for a league/season then get it from
       upstream and fill the database'''
    session = Session()
    print "creating local league object for %s %s"%(league,season)
    l = League(league,season)
    session.add(l)
    print "getting upstream matchdata for %s %d. This could take a while..."%(league,season)
    try:
      remote = self.oldb.GetMatchdataByLeagueSaison(league,season)
    except Exception,e:
      print e
      raise
    else:
      print "retrieved upstream data. Parsing..."
      for m in remote.Matchdata:
        self.mergeRemoteLocal(m)

  def localCacheValid(self,league=None,season=None):
    '''Check to see if the local cache is behind openligadb.de.
    '''
    if not league:
      league = DEFAULT_LEAGUE
    if not season:
      season = current_bundesliga_season()
    session = Session()
    print "Checking local cache for %s %d"%(league,season)
    try:
      remote_tstamp = self.oldb.GetLastChangeDateByLeagueSaison(league,season)
    except Exception,e:
      print e
      print "SOAP Error for league %s season %s?"%(str(league),str(season))
      return False
    else:
      local_league=session.query(League).filter(and_(League.season==season,League.name==league)).first()
      if not local_league:
        print "No locally stored league for %s %d"%(league,season)
        return False
      last_match_change = session.query(Match.mtime).order_by(Match.mtime.desc()).first()
      last_goal_change = session.query(Goal.mtime).order_by(Goal.mtime.desc()).first()
      if not last_match_change or not last_goal_change:
        print "None objects returned when querying mtimes for match, matchday, goal"
        return False
      elif last_match_change.mtime < remote_tstamp or last_goal_change.mtime < remote_tstamp:
        print "Upstream tstamp: %s"%remote_tstamp
        print "Match tstamp: %s"%last_match_change.mtime
        print "Goal tstamp: %s"%last_goal_change.mtime
        print "Local data exists but at least one required table is out of date"
        return False
      else:
        print "Local data exists and is up to date"
        return True

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
    remote_tstamp = self.oldb.GetLastChangeDateByLeagueSaison(league,season)
    if not self.localCacheValid(league,season):
      self.setupLocal(league,season)
    if client_tstamp:
      q = session.query(Match).filter(and_(Match.league==league,Match.season==season,
           or_(Match.startTime >= client_tstamp,and_(Match.startTime <= client_tstamp,Match.endTime >= client_tstamp))))
    else:
      q = session.query(Match).join(League).filter(and_(League.name==league,League.season==season))
    local_matchdata = q.all()
    return local_matchdata

  def updateMatchByID(self,matchID):
    print "I've been asked to update matchID %d"%matchID
    try:
      print "Asking upstream for the most recent data for matchID %d"%matchID
      remote = self.oldb.GetMatchByMatchID(matchID)
    except:
      raise
    else:
      print "Received upstream data...handing over to mergeRemoteLocal()"
      self.mergeRemoteLocal(remote)

  def getMatchesByMatchday(self,league,season,matchday):
    session = Session()
    matches = session.query(Match).join(League).filter(and_(League.name==league,League.season==season,
                    Match.matchday==matchday)).all()
    return matches

  def updateMatchday(self,league,season,matchday):
    for match in self.getMatchesByMatchday(league,season,matchday):
      print "Updating matchID %d"%match.id
      self.updateMatchByID(match.id)

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
            team = session.merge(Team(t.teamID,t.teamName.encode('utf-8'),t.teamIconURL))
            team.leagues.append(local_league)
          session.commit()
      teams = local_league.teams
    else:
      session.commit()
      print "There are 18 teams. Everything ok..."
    finish = time.time()
    print "<Running method getTeams() took %f seconds>"%(finish-start)
    return teams

  def localMatchdayValid(self,league,season,matchday):
    '''Check if a particular matchday is up to date. Useful to call when the match is actually
       running and is a good candidate to run before updating the local matchdays'''
    session = Session()
    lastlocal = session.query(Match.mtime).join(League).filter(and_(League.season==season,
           League.name==league,Match.matchday==matchday)).order_by(Match.mtime.desc()).first()
    lastremote = self.oldb.GetLastChangeDateByGroupLeagueSaison(matchday,league,season)
    if lastremote > lastlocal[0]:
      return False
    else:
      return True
         
  def mergeRemoteLocal(self,m):
    print "I've been asked to merge data for matchID %d"%m.matchID
    session = Session()
    l = session.merge(League(m.leagueShortcut,int(m.leagueSaison)))
    d = timedelta(minutes=115) # estimate when the match will end
    estEnd = m.matchDateTime+d
    if m.NumberOfViewers:
      viewers = m.NumberOfViewers
    else:
      viewers = 0
    match = session.merge(Match(m.matchID,m.groupOrderID,m.matchDateTime,estEnd,m.matchIsFinished,viewers))
    t1 = session.merge(Team(m.idTeam1,m.nameTeam1.encode('utf-8'),m.iconUrlTeam1))
    t2 = session.merge(Team(m.idTeam2,m.nameTeam2.encode('utf-8'),m.iconUrlTeam2))
    match.teams.append(t1)
    match.teams.append(t2)
    l.teams.append(t1)
    l.teams.append(t2)
    t1.leagues.append(l)
    t2.leagues.append(l)
    l.matches.append(match)
    print "Finished parsing the matches. Now parsing the upstream goaldata..."
    for goals in m.goals:
      for goal in goals:
        for goalobj in goal:
          if hasattr(goalobj,'goalID'):
            if hasattr(goalobj,'goalGetterName'):
              scorer = goalobj.goalGetterName.encode('utf-8')
            else:
              scorer = u'Unknown'
            localGoal = session.merge(Goal(goalobj.goalID,scorer,
                            goalobj.goalMatchMinute,goalobj.goalScoreTeam1,goalobj.goalScoreTeam2,
                            goalobj.goalOwnGoal,goalobj.goalPenalty,))
            match.goals.append(localGoal)
    for goal in match.goals:# now try to find out what team scored. not easy from raw openligadb data
      if match.goals.index(goal) == 0:#the first goal is easy
        if match.goals[0].t1score == 1:
          match.goals[0].for_team_id = match.teams[0].id
        else:
          match.goals[0].for_team_id = match.teams[1].id
      else:#look to the last goal to see whose score increased
        prev1 = match.goals[match.goals.index(goal)-1].t1score
        prev2 = match.goals[match.goals.index(goal)-1].t2score
    print "Committing the session..."
    session.commit()
