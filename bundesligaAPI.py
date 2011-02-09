# -*- coding: utf-8 -*-
from OpenLigaDB import OpenLigaDB
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_,or_,not_
from bundesligaORM import *
from bundesligaHelpers import shortcuts,tstamp_to_md5
from bundesligaLogger import logger
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

class StaleData(Exception):
  '''Raise this exception to let the calling script know that it has been 
     detected that the local dataset is stale and that an update is requested
     from upstream. Let the calling script decide on whether or not to
     immediately perform the update (e.g. in background thread)
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

  def localLeagueSeason(self,league,season):
    session=Session()
    l = session.query(League).filter(and_(League.name==league,League.season==season)).first()
    if not l:
      return False
    else:
      return l

  def updateLocalCache(self,league,season):
    '''Rather than rewriting the entire database for a league and season ask
       upstream for only enough data to sync the local database.'''
    if not league:
      logger.info("updateLocalCache - no league sent. using default...")
      league = DEFAULT_LEAGUE
    if not season:
      logger.info("updateLocalCache - no season sent. using default...")
      season = current_bundesliga_season()
    # now get matchIDs from league,season where match not over
    session = Session()
    now = datetime.now() # no point in updating the future
    l = session.query(League).filter(and_(League.season==season,League.name==league)).first()
    if not l:
      logger.info("updateLocalCache - no local cache for league %s season %d. Running setupLocal()..."%(league,season))
      self.setupLocal(league,season)
    matches = session.query(Match.id).join(League).filter(and_(League.season==season,\
                League.name==league,Match.isFinished==False,Match.startTime <= now)).all()
    logger.info("updateLocalCache - %d matches in update window..."%len(matches))
    for matchID in matches:
      logger.info("updateLocalCache - updating matchID %d..."%matchID)
      self.updateMatchByID(matchID)

  def getUpdatesByTstamp(self,league,season,tstamp):
    if not league:
      league = DEFAULT_LEAGUE
    if not season:
      season = current_bundesliga_season()
    if not tstamp:
      tstamp = datetime.now()
    logger.info("getUpdatesByTstamp - looking for updates for %s %d since %s"%(league,season,tstamp))
    l = self.localLeagueSeason(league,season)
    if not l:
      logger.info("getUpdatesByTstamp - no league/season data for %s %d. Running setupLocal()"%(league,season))
      raise StaleData,"No league/season data for %s %d. Try running setupLocal()"%(league,season)
    # now get anything that has happened since client's tstamp
    session = Session()
    now = datetime.now()
    updates = session.query(Match).join(League).filter(and_(League.season==season,\
                 League.name==league,and_(Match.startTime<=now,and_(Match.endTime >= tstamp,Match.endTime <= now)))).all()
    goals = {}
    goalindex = {}
    for match in updates:
      if match.isFinished:
        if len(match.goals):
          for g in match.goals:
            goals[g.id] = {'scorer':g.scorer.encode('utf-8'),'minute':g.minute,'penalty':g.penalty,'ownGoal':g.ownGoal,'teamID':g.for_team_id}
          goalindex[match.id] = [x.id for x in match.goals]
          goalindex[match.id].append(True)
        else:
          goalindex[match.id] = [None,True]
      else:
        if len(match.goals):
          for g in match.goals:
            goals[g.id] = {'scorer':g.scorer.encode('utf-8'),'minute':g.minute,'penalty':g.penalty,'ownGoal':g.ownGoal,'teamID':g.for_team_id}
          goalindex[match.id] = [x.id for x in match.goals]
          goalindex[match.id].append(False)
        else:
          goalindex[match.id] = [False]
    rd = (goals,goalindex)
    return rd


  def getUpdatesByMatchday(self,league,season,matchday=None):
    '''Client sends a league, season and matchday. All of these values can be empty
       or None. If the values are empty or none, we choose defaults. If the client
       sends a matchday (valid matchdays are between 1 and 34 inclusive) then we only
       check for updates for that particular matchday. If no matchday is sent then we
       check for updates for current matchday.
    '''
    if not league:
      league = DEFAULT_LEAGUE
    if not season:
      season = current_bundesliga_season()
    if not matchday:
      matchday = current_bundesliga_matchday()
      logger.info("getUpdatesByMatchday - no matchday sent. Using current bundesliga matchday which is %d"%matchday)
    else:
      if matchday not in range(1,35):
        matchday = current_bundesliga_matchday()
        logger.info("getUpdatesByMatchday - invalid matchday sent (not in range(1,35)). Using current bundesliga matchday which is %d"%matchday)
    l = self.localLeagueSeason(league,season)
    if not l:
      logger.info("getUpdatesByMatch - no league/season data for %s %d. Running setupLocal()"%(league,season))
      self.setupLocal(league,season)
    else:
      logger.info("getUpdatesByMatch - have league/season data for %s %d..."%(league,season))
    #check validity of local cache for matchday
    #if not self.localMatchdayValid(league,season,matchday):
    #  logger.info("getUpdatesByMatch - local data for matchday %d no valid. Updating..."%matchday)
    #  self.updateMatchday(league,season,matchday)
    session = Session()
    updates = session.query(Match).join(League).filter(and_(League.season==season,League.name==league,Match.matchday==matchday)).all()
    goals = {}
    goalindex = {}
    for match in updates:
      if match.isFinished:
        if len(match.goals):
          for g in match.goals:
            goals[g.id] = {'scorer':g.scorer.encode('utf-8'),'minute':g.minute,'penalty':g.penalty,'ownGoal':g.ownGoal,'teamID':g.for_team_id}
          goalindex[match.id] = [x.id for x in match.goals]
          goalindex[match.id].append(True)
        else:
          goalindex[match.id] = [None,True]
      else:
        if len(match.goals):
          for g in match.goals:
            goals[g.id] = {'scorer':g.scorer.encode('utf-8'),'minute':g.minute,'penalty':g.penalty,'ownGoal':g.ownGoal,'teamID':g.for_team_id}
          goalindex[match.id] = [x.id for x in match.goals]
          goalindex[match.id].append(False)
        else:
          goalindex[match.id] = [False]

    rd = (goals,goalindex)
    return rd

  def setupLocal(self,league,season):
    '''If there is no local data available for a league/season then get it from
       upstream and fill the database'''
    session = Session()
    logger.info("setupLocal - creating local league object for %s %s"%(league,season))
    l = League(league,season)
    session.add(l)
    logger.info("setupLocal - getting upstream matchdata for %s %d. This could take a while..."%(league,season))
    try:
      remote = self.oldb.GetMatchdataByLeagueSaison(league,season)
    except Exception,e:
      logger.info("setupLocal - pull from upstream failed because: %s"%str(e))
      raise
    else:
      logger.info("setupLocal - retrieved upstream data. Parsing...")
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
    logger.info("localCacheValid - checking local cache for %s %d"%(league,season))
    try:
      remote_tstamp = self.oldb.GetLastChangeDateByLeagueSaison(league,season)
    except Exception,e:
      logger.info("localCacheValid - SOAP Error for league %s season %s?"%(str(league),str(season)))
      return False
    else:
      local_league=session.query(League).filter(and_(League.season==season,League.name==league)).first()
      if not local_league:
        logger.info("localCacheValid - no locally stored league for %s %d"%(league,season))
        return False
      last_match_change = session.query(Match.mtime).order_by(Match.mtime.desc()).first()
      last_goal_change = session.query(Goal.mtime).order_by(Goal.mtime.desc()).first()
      if not last_match_change or not last_goal_change:
        logger.info("localCacheValid - None objects returned when querying mtimes for match, matchday, goal")
        return False
      elif last_match_change.mtime < remote_tstamp or last_goal_change.mtime < remote_tstamp:
        logger.info("localCacheValid - local data exists but at least one required table is out of date")
        return False
      else:
        logger.info("localCacheValid - local data exists and is up to date")
        return True

  def getMatchdataByLeagueSeason(self,league,season):
    '''Return a dictionary holding data for matches returned for an entire
       season where the keys of the dictionary are the matchdays. The values
       are dictionaries containing the matchdata. If the client's tstamp is
       specified we additionally check if we can return an empty dataset - i.e
       if the client's tstamp indicates that the client's dataset is already
       up to date, then to save bandwidth we return an empty set
    '''
    s = time.time()
    session=Session()
    remote_tstamp = self.oldb.GetLastChangeDateByLeagueSaison(league,season)
    logger.info("getMatchdataByLeagueSeason - upstream tstamp for league=%s season=%s is %s"%(league,str(season),remote_tstamp))
    # TODO: decide if these lines can stay commented out. If the partialSync script is run by cron
    # then we have reason to expect that the local cache will be always valid
    #if not self.localCacheValid(league,season):
    #  logger.info("getMatchdataByLeagueSeason - local cache not valid. Need to run setupLocal")
    #  self.setupLocal(league,season)
    q = session.query(Match).join(League).filter(and_(League.name==league,League.season==season))
    local_matchdata = q.all()
    e = time.time()
    t = e-s
    logger.info("getMatchdataByLeagueSeason - found %d match data objects for league=%s \
season=%s. Took %f seconds"%(len(local_matchdata),league,str(season),t))
    return local_matchdata

  def updateMatchByID(self,matchID):
    try:
      logger.info("updateMatchByID - asking upstream for the most recent data for matchID %d"%matchID)
      remote = self.oldb.GetMatchByMatchID(matchID)
    except:
      raise
    else:
      logger.info("updateMatchByID - received upstream data...handing over to mergeRemoteLocal()")
      self.mergeRemoteLocal(remote)

  def getMatchesByMatchday(self,league,season,matchday):
    session = Session()
    matches = session.query(Match).join(League).filter(and_(League.name==league,League.season==season,
                    Match.matchday==matchday)).all()
    return matches

  def updateMatchday(self,league,season,matchday):
    for match in self.getMatchesByMatchday(league,season,matchday):
      self.updateMatchByID(match.id)

  def getMatchdataByMatchID(self,matchID):
    pass

  def getGoalsByMatchID(self,matchID):
    pass

  def getGoalsByLeagueSeason(self,league,season):
    '''Return a tuple containing a dictionary of goal objects where the keys are
       the goalIDs. The second element in the tuple is a dictionary where the 
       keys are matchIDs and the values are lists containing pointers to the goalID
    '''
    logger.info("getGoalsByLeagueSeason called with league=%s and season=%d"%(league,season))
    s = time.time()
    now = datetime.now()
    session = Session()
    g = session.query(Goal).join(Match).join(League).filter(and_(League.season==season,
                            League.name==league)).all()
    goalindex,goalobjects = {},{}
    logger.info("getGoalsByLeagueSeason - found %d goal objects for league %s season %d"%(len(g),league,season))
    for goal in g:
      if not goalindex.has_key(goal.match.id):
        goalindex[goal.match.id] = []
      goalobjects[goal.id] = {'scorer':goal.scorer.encode('utf-8'),'minute':goal.minute,
                              'penalty':goal.penalty,'ownGoal':goal.ownGoal,'teamID':goal.for_team_id}
      goalindex[goal.match.id].append(goal.id)
    e = time.time()
    total = e-s
    logger.info("getGoalsByLeagueSeason - finished in %f seconds"%total)
    return (goalobjects,goalindex)

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
      logger.info("getTeams - number of teams in %s for season %d is %d: UPDATING"%(league,season,len(teams)))
      try:
        remote_teams = self.oldb.GetTeamsByLeagueSaison(league,season)
      except WebFault,e:
        raise InvocationError, "SOAP client could not complete request. Check parameters!"
      else:
        for t in remote_teams.Team:
          if not t.teamIconURL and t.teamID > 250:
            logger.info("getTeams - ignoring %s as it doesn't seem to be a real team"%(t.teamName.encode('utf-8')))
          else:
            team = session.merge(Team(t.teamID,t.teamName.encode('utf-8'),t.teamIconURL))
            team.leagues.append(local_league)
          session.commit()
      teams = local_league.teams
    else:
      session.commit()
    finish = time.time()
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
    session = Session()
    l = session.merge(League(m.leagueShortcut,int(m.leagueSaison)))
    d = timedelta(minutes=115) # estimate when the match will end
    estEnd = m.matchDateTime+d
    if m.NumberOfViewers:
      viewers = m.NumberOfViewers
    else:
      viewers = 0
    match = session.merge(Match(m.matchID,m.groupOrderID,m.matchDateTime,estEnd,m.matchIsFinished,\
                           m.pointsTeam1,m.pointsTeam2,viewers))
    t1 = session.merge(Team(m.idTeam1,m.nameTeam1.encode('utf-8'),m.iconUrlTeam1))
    t2 = session.merge(Team(m.idTeam2,m.nameTeam2.encode('utf-8'),m.iconUrlTeam2))
    match.teams.append(t1)
    match.teams.append(t2)
    l.teams.append(t1)
    l.teams.append(t2)
    t1.leagues.append(l)
    t2.leagues.append(l)
    l.matches.append(match)
    for goals in m.goals:
      for goal in goals:
        for goalobj in goal:
          if hasattr(goalobj,'goalID'):
            if hasattr(goalobj,'goalGetterName'):
              scorer = goalobj.goalGetterName.encode('utf-8')
            else:
              scorer = u'Unknown'
            if goalobj.goalPenalty == None or goalobj.goalPenalty == False: #sometimes null sometimes False
              penalty = False
            localGoal = session.merge(Goal(goalobj.goalID,scorer,
                            goalobj.goalMatchMinute,goalobj.goalScoreTeam1,goalobj.goalScoreTeam2,
                            goalobj.goalOwnGoal,goalobj.goalPenalty,))
            match.goals.append(localGoal)
    for goal in match.goals:# now try to find out what team scored. not easy from raw openligadb data
      cur_idx = match.goals.index(goal)
      if cur_idx == 0:#the first goal is easy
        if match.goals[0].t1score == 1:
          match.goals[0].for_team_id = match.teams[0].id
        else:
          match.goals[0].for_team_id = match.teams[1].id
      else:#look to the last goal to see whose score increased
        prev1 = match.goals[cur_idx-1].t1score
        prev2 = match.goals[cur_idx-1].t2score
        if match.goals[cur_idx].t1score > prev1:
          match.goals[cur_idx].for_team_id = match.teams[0].id
        else:
          match.goals[cur_idx].for_team_id = match.teams[1].id
    session.commit()
