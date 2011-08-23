# -*- coding: utf-8 -*-
from orm import *
from OpenLigaDB import OpenLigaDB
from sqlalchemy.sql import and_, or_, not_
from datetime import datetime
from PermaData import DEFAULT_LEAGUE,getCurrentMatchDay,getCurrentSeason,\
    DBASE
import os,json

oldb = OpenLigaDB()

class Dictify:
  def dictifyTeam(self,team):
    t={'fullName':team.fullName.encode('utf-8'),
       'iconURL':team.iconURL,
       'id':int(team.id),
       'shortName':team.shortName}
    return t
    
  def dictifyGoal(self,goal):
    t={ 'id':int(goal.id),
        'scorer':goal.scorer.encode('utf-8'),
        'minute':int(goal.minute),
        'wasPenalty':goal.wasPenalty,
        'wasOwnGoal':goal.wasOwnGoal}
    return t
    
  def dictifyMatch(self,match):
    t={ 'id':int(match.id),
        'isFinished':match.isFinished,
        'matchDay':int(match.matchDay),
        'startTime':match.startTime.strftime("%Y-%m-%d %H:%M"),
        'viewers':int(match.viewers),
        'location':match.location,
        'team1': self.dictifyTeam(match.team1),
        'team2': self.dictifyTeam(match.team2),
        'goals': [self.dictifyGoal(x) for x in match.goals],
      }
    
    return t
        
    
  def dictifyLeague(self,league):
    t={ 'id':int(league.id),
        'name':league.name.encode('utf-8'),
        'shortcut':league.shortcut,
        'season':int(league.season)}
    return t

class localService:

  def __init__(self):
    self.dictifier = Dictify()
    
  def getLastUpstreamChange(self,league=DEFAULT_LEAGUE,
        season=getCurrentSeason()):
    ''' @league:  string representing shortname of league (e.g. 'bl1')
        @season:  int representing year (e.g. 2011)
        @returns: datetime of last change of upstream database
    '''
    lastchange = oldb.GetLastChangeDateByLeagueSaison(league,season)
    return lastchange
    
  def getLastLocalChange(self):
    ''' Simple method which uses os.stat to get the last modification of
        the local sqlite file. This is (obviously) the last change to the
        database
    '''
    dbase_abspath = os.path.abspath(os.path.join(os.getcwd(),DBASE))   
    lastchange = datetime.fromtimestamp(os.stat(dbase_abspath)[8])
    return lastchange    
    
  def getLeagueByShortcutSeason(self,league,season,ret_dict=True):
    session = Session()
    try:
      league = session.query(League).filter(and_(League.shortcut==league,
                League.season==season)).one()
    except:
      raise
    else:
      if ret_dict:
        return self.dictifier.dictifyLeague(league)
      else:
        return league
    finally:
      session.close()
        
  def getLeagueByID(self,leagueID,ret_dict=True):
    session=Session()
    try:
      league = session.query(League).filter(League.id==leagueID).one()
    except:
      raise
    else:
      if ret_dict:
        return self.dictifier.dictifyLeague(league)
      else:
        return league
    finally:
      session.close()
      
  def getMatchByID(self,matchID,ret_dict=True):
    session = Session()
    try:
      match = session.query(Match).filter(Match.id==matchID).one()
    except:
      raise
    else:
      if ret_dict:
        return self.dictifier.dictifyMatch(match)
      else:
        return match
    finally:
      session.close()
      
  def getMatchesInProgressNow(self,ret_dict=True):
    session=Session()
    try:
      mip = session.query(Match).filter(and_(Match.isFinished != True,
            Match.startTime<=datetime.now())).all()
    except:
      raise
    else:
      if ret_dict:
        matchlist = []
        for m in mip:
          matchlist.append(self.dictifier.dictifyMatch(m))
        return matchlist
      else:
        return mip
    finally:
      session.close()
      
  def getMatchesInProgressAsOf(self,tstamp=datetime.now(),ret_dict=True):
    ''' @tstamp:  datetime representing tstamp as of which requestor wants
                  to know if a match is in progress.
        This method takes a datetime and checks if any Match has a startTime
        from datetime-100 minutes to datetime. The 100 minutes is a randomly
        chosen time which generally will address all bundesliga games.
    '''
    from datetime import timedelta
    matchdelta = timedelta(minutes=-100)
    earlylimit = tstamp+matchdelta
    session = Session()
    try:
      mip = session.query(Match).filter(and_(Match.startTime>=earlylimit,
            Match.startTime<=tstamp)).all()
    except:
      raise
    else:
      if ret_dict:
        matchlist = []
        for m in mip:
          matchlist.append(self.dictifier.dictifyMatch(m))
        return matchlist
      else:
        return mip
    finally:
      session.close()
    
  def getGoalByID(self,goalID,ret_dict=True):
    session = Session()
    try:
      goal = session.query(Goal).filter(Goal.id==goalID).one()
    except:
      raise
    else:
      if ret_dict:
        return self.dictifier.dictifyGoal(goal)
      else:
        return goal
    finally:
      session.close()

  def getTeams(self,league=DEFAULT_LEAGUE,season=getCurrentSeason(),
              ret_dict=True):
    session = Session()
    try:
      league = session.query(League).filter(and_(League.season==season,
            League.shortcut==league)).one()
    except:
      raise
    else:
      teamlist = []
      for team in league.teams:
        if ret_dict:
          teamlist.append(self.dictifier.dictifyTeam(team))
        else:
          teamlist.append(team)
      return teamlist
    finally:
      session.close()
    

  def getTeamByID(self,teamID,ret_dict=True):
    session = Session()
    try:
      team = session.query(Team).filter(Team.id==teamID).one()
    except:
      raise
    else:
      if ret_dict:
        return self.dictifier.dictifyTeam(team)
      else:
        return team
    finally:
      session.close()
      
  def getTeamByShortname(self,shortName,ret_dict=True):
    session = Session()
    try:
      team = session.query(Team).filter(Team.shortName==shortName).one()
    except:
      raise
    else:
      if ret_dict:
        return self.dictifier.dictifyTeam(team)
      else:
        return team
    finally:
      session.close()      
      
  def getGoalsSince(self,ret_dict=True):
    pass

  def getMatchesByMatchday(self,matchday=getCurrentMatchDay(),
        league=DEFAULT_LEAGUE,season=getCurrentSeason(),ret_dict=True):
    '''
    '''
    session = Session()
    try:
      matches = session.query(Match).join(League).filter(and_(Match.matchDay==matchday,
                  League.shortcut==league,
                  League.season==season)).all()
    except:
      raise
    else:
      if ret_dict:
        matchlist = []
        for match in matches:
          matchlist.append(self.dictifier.dictifyMatch(match))
        return matchlist
      else:
        return matches
    finally:
      session.close()
      
  def getGoalByID(self,goalID,ret_dict=True):
    session = Session()
    try:
      goal = session.query(Goal).filter(Goal.id==goalID).one()
    except:
      raise
    else:
      if ret_dict:
        return self.dictifier.dictifyGoal(goal)
      else:
        return goal
    finally:
      session.close()
