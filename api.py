# -*- coding: utf-8 -*-

'''
Copyright (c) 2011, Ciaran Farrell, Vladislav Lewin
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

Neither the name of the authors nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
from orm import *
from OpenLigaDB import OpenLigaDB
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy import func,desc
from datetime import datetime
from PermaData import getCurrentMatchDay,getCurrentSeason,DBASE,getDefaultLeague
import os,json,time
oldb = OpenLigaDB()

class Dictify:
  ''' This Dictify class is to make it easier to convert objects returned from
      SQLAlchemy queries into dictionaries. This is necessary because when
      responding to queries over web.py we usually return JSON. JSON is
      particularly sensitive to certain data types such as datetime. In order to
      avoid JSON encoding errors, we convert to dictionary and also convert
      certain datatypes to a more JSON friendly type
  '''
  
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
        'half':int(goal.half),
        'estTstamp':goal.estTstamp.strftime("%Y-%m-%d %H:%M"),
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
    
  def getLastUpstreamChange(self,league=getDefaultLeague(),
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
    
  def getLastChangeToMatches(self):
    ''' @returns: datetime of last modification to Match table
    '''
    session = Session()
    try:
      lastmod = session.query(func.max(Match.modified)).one()
    except:
      raise
    else:
      return lastmod[0]
    finally:
      session.close()
    
  def getLeagueByShortcutSeason(self,league=getDefaultLeague(),
            season=getCurrentSeason(),ret_dict=True):
    ''' @league:  string representing shortcut of League (e.g. 'bl1')
        @season:  int representing season year (e.g. 2011)
        @returns: dictionary representing League object, or the League object
                  itself if caller uses ret_dict = False
    '''
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
    ''' @matchID: int representing primary key of the League object in the
                  database.
        @returns: dictionary representing League object, or the League object
                  itself if caller uses ret_dict = False
    ''' 
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

  def getLeagues(self,ret_dict=True):
    ''' @returns: list of dictionaries representing League objects or League
        objects if caller uses ret_dict=False
    '''
    session=Session()
    try:
      leagues = session.query(League).all()
    except:
      raise
    else:
      if ret_dict:
        leaguelist = []
        for league in leagues:
          leaguelist.append(self.dictifier.dictifyLeague(league))
        return leaguelist
      else:
        return leagues
    finally:
      session.close()
        
  def getMatchByID(self,matchID,ret_dict=True):
    ''' @matchID: int representing primary key of the Match object in the
                  database.
        @returns: dictionary representing Match object, or the Match object
                  itself if caller uses ret_dict = False
    '''
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
      
  def getMatchesInProgressNow(self,league=getDefaultLeague(),ret_dict=True):
    ''' A simple method to find out from the local database which matches are
        in progress at the moment (if any)
        @returns: List of Match dictionaries or list of Match objects if the
                  caller uses ret_dict = False
    '''
    session=Session()
    try:
      mip = session.query(Match).join(League).filter(\
            and_(Match.isFinished!=True,Match.startTime<=datetime.now(),
            League.shortcut==league)).all()
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
      
  def getMatchesInProgressAsOf(self,tstamp=datetime.now(),
        league=getDefaultLeague(),ret_dict=True):
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
      mip = session.query(Match).join(League).filter(\
            and_(Match.startTime>=earlylimit,League.shortcut==league,
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
    ''' @goalID:  int representing primary key of Goal object in database
        @returns: dictionary representing Goal object or Goal object itself if
                  caller uses ret_dict=False
    '''
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

  def getTeams(self,league=None,season=None,
              ret_dict=True):
    ''' @league:  string representing League shortcut (e.g. 'bl1')
        @season:  int representing season year (e.g. 2011)
        @returns: list of Dictionaries representing Team objects or Team objects
                  if caller uses ret_dict=False
    '''
    session = Session()
    if not league and season:
      try:
        leagues = session.query(League).filter(League.season==season).all()
      except:
        raise
    elif league and not season:
      try:
        leagues = session.query(League).filter(League.shortcut==league).all()
      except:
        raise
    elif not league and not season:
      try:
        leagues = session.query(League).all()
      except:
        raise
    else:
      try:
        leagues = session.query(League).filter(and_(League.season==season,
            League.shortcut==league)).all()
      except:
        raise
    teamlist = []
    for league in leagues:
      for team in league.teams:
        if ret_dict:
          dictteam = self.dictifier.dictifyTeam(team)
          if dictteam not in teamlist:
            teamlist.append(dictteam)
        else:
          if team not in teamlist:
            teamlist.append(team)
    session.close()
    return teamlist
    

  def getTeamByID(self,teamID,ret_dict=True):
    ''' @teamID:  int representing primary key of Team object in database
        @retuns:  dictionary representing Team object or Team object itself if
                  caller uses ret_dict=False
    '''
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
    ''' @shortName: string representing Team shortName (e.g. '1FCN')
        @returns:   dictionary representing Team object or Team object if
                    caller uses ret_dict=False
    '''
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
      
  def getGoalsSince(self,tstamp,ret_dict=True):
    ''' TODO: retrieve goals since tstamp
    '''
    pass

  def getMatchesByMatchday(self,matchday=getCurrentMatchDay(),
        league=getDefaultLeague(),season=getCurrentSeason(),ret_dict=True):
    ''' @matchday:  int representing bundesliga matchday (e.g. max 34)
        @league:    string representing League shortcut (e.g. 'bl1')
        @season:    int representing season year (e.g. 2011)
        @returns:   list of dictionaries representing Match objects or list oft
                    Match objects if caller uses ret_dict=False
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
    ''' @goalID:  int representing primary key of Goal object in database
        @returns: dictionary representing Goal object or Goal object if caller
                  uses ret_dict=False
    '''
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
      
  def getGoalsSince(self,tstamp,matchlist,ret_dict=True):
    ''' @matchlist: list of Match objects
        @tstamp:    datetime
    '''
    session = Session()
    #TODO this loop is not needed. Find out how to use in_
    goaldict =  {}
    print "api:localService:getGoalsSince\
              with tstamp %s"%tstamp.strftime("%Y-%m-%d %H:%M")
    for match in matchlist:
      goaldict[match.id] = []
      goals = session.query(Goal).join(Match).filter(and_(Match.id==match.id,
              Goal.modified > tstamp)).all()
      print "%d goals in match with id %d since %s"%(len(goals),match.id,
              tstamp.strftime("%Y-%m-%d %H:%M"))
      for goal in goals:
        if ret_dict:
          goaldict[match.id].append(self.dictifier.dictifyGoal(goal))
        else:
          goaldict[match.id].append(goal)
    session.close()
    return goaldict
    
  def getMatchesSinceGoalID(self,maxid,league=getDefaultLeague(),ret_dict=True):
    ''' @maxid:   int representing the highest goal id that the requestor
                  currently has.
        @league:  filter only goals from a certain League
        @returns: list of dictionaries representing Goals entered into local
                  database since maxid
    '''
    session = Session()
    matches = session.query(Match).join(League).join(Goal).filter(and_(
            Goal.id > maxid,League.shortcut==league)).all()
    if ret_dict:
      matchlist = []
      for match in matches:
        matchlist.append(self.dictifier.dictifyMatch(match))
      return matchlist
    else:
      return matches
    session.close()
    
  def getMaxGoalID(self,league=getDefaultLeague()):
    ''' @league:  string representing shortcut of League object (e.g. 'bl1')
        @returns: int of maxid in Goal table for league
    '''
    session = Session()
    maxgoal = session.query(Goal).join(Match).\
          join(League).filter(League.shortcut == league).order_by(\
          Goal.id.desc()).all()
    session.close()
    if not len(maxgoal):
      raise StandardError, 'No goals found'
    else:
      return int(maxgoal[0].id)
    
  def getMatchGoalsSinceGoalID(self,maxid,ret_dict=True):
    session = Session()
    goals = session.query(Goal).filter(Goal.id > maxid).all()
    matches = {}
    for g in goals:
      if not matches.has_key(g.match.id):
        if ret_dict:
          matches[g.match.id] =  [self.dictifier.dictifyGoal(g)]
        else:
          matches[g.match.id] =  [g]
      else:
        if ret_dict:
          matches[g.match.id].append(self.dictifier.dictifyGoal(g))
        else:
          matches[g.match.id].append(g)
    session.close()
    return matches
    
  def getGoalsSinceID(self,goal_id,league=getDefaultLeague(),ret_dict=True):
    session = Session()
    goals = session.query(Goal).join(Match).join(League).filter(and_(\
            Goal.id>goal_id,League.shortcut == league)).all()
    if ret_dict:
      goallist =  []
      for g in goals:
        goallist.append(self.dictifier.dictifyGoal(g))
      return goallist
    else:
      return goals
    session.close()
    
  def getGoalsPerMatchWithFlags(self,max_goal_id,league=getDefaultLeague()):
    mip = self.getMatchesInProgressNow(league=league)
    newgoals = self.getGoalsSinceID(max_goal_id,league,ret_dict=False)
    matches = {}
    for m in mip:
      if not matches.has_key(m['id']):
        matches[m['id']] = []
      for goaldict in m['goals']:
        if goaldict['id'] in [x.id for x in newgoals]:
          goaldict['isNew'] = True
        else:
          goaldict['isNew'] = False
        matches[m['id']].append(goaldict)
    return matches
    
  def getPointsPerTeam(self,team_id,league=getDefaultLeague(),
        season=getCurrentSeason(),matchday=getCurrentMatchDay()):
      session=Session()
      matches = session.query(Match).join(League).filter(\
            and_(League.shortcut==league,
            League.season==season,Match.matchDay<=matchday,
            or_(Match.matchTeam1==team_id,
            Match.matchTeam2==team_id))).all()
      goals_for,goals_against,points,won,drew,lost = 0,0,0,0,0,0
      for match in matches:
        if match.matchTeam1 == team_id:
          goals_for += len(match.team1goals)
          goals_against += len(match.team2goals)
          if len(match.team1goals) > len(match.team2goals):
            points+=3
            won+=1
          elif len(match.team1goals) == len(match.team2goals):
            points+=1
            drew+=1
          else:
            lost+=1
        elif match.matchTeam2 == team_id:
          goals_for += len(match.team2goals)
          goals_against += len(match.team1goals)
          if len(match.team2goals) > len(match.team1goals):
            points+=3
            won+=1
          elif len(match.team2goals) == len(match.team1goals):
            points+=1
            drew+=1
          else:
            lost+=1
        else:
          raise StandardError, "wtf?! Cannot be..."
      session.close()
      return {'goals_for':goals_for,'goals_against':goals_against,
              'points':points,'won':won,'drew':drew,'lost':lost,
              'played':len(matches),
              'difference':goals_for-goals_against,'team_id':team_id}
            
          
  def test(self,matchday,league=getDefaultLeague(),season=getCurrentSeason()):
    start=time.time()
    session=Session()
    if season > getCurrentSeason():
      raise StandardError, "not possible to query future season tables"
    elif season == getCurrentSeason() and matchday > getCurrentMatchDay():
      raise StandardError, "not possible to query future match days"
    else:
      teams = {}
      matches = session.query(Match).join(League).filter(\
        and_(League.season==season,
        League.shortcut==league,Match.matchDay<=matchday)).all()
      for match in matches:
        t1,t2 = match.team1.id,match.team2.id
        if not teams.has_key(t1):
          teams[t1] = {'gf':0,'ga':0,'points':0,'w':0,'l':0,'d':0,}
        if not teams.has_key(t2):
          teams[t2] = {'gf':0,'ga':0,'points':0,'w':0,'l':0,'d':0,}
        if len(match.team1goals) > len(match.team2goals):
          teams[t1]['points']+=3
          teams[t1]['w']+=1
          teams[t2]['l']+=1
        elif len(match.team1goals) < len(match.team2goals):
          teams[t2]['points']+=3
          teams[t2]['w']+=1
          teams[t1]['l']+=1
        else:
          teams[t1]['points']+=1
          teams[t2]['points']+=1
          teams[t1]['d']+=1
          teams[t2]['d']+=1
        teams[t1]['gf']+=len(match.team1goals)
        teams[t2]['gf']+=len(match.team2goals)
        teams[t1]['ga']+=len(match.team2goals)
        teams[t2]['ga']+=len(match.team1goals) 
    end=time.time()
    took = end-start
    print "%.3f seconds"%took
    return teams
    session.close()
