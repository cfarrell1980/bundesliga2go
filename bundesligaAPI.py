from pymongo import Connection,ASCENDING
from pymongo.code import Code
from datetime import datetime
from bundesligaGlobals import *
connection = Connection()
db = connection.bundesliga2go
bl_1 = db.bl1_2011

class bundesligaAPI:

  def test(self):
    #count all goals?
    map = Code( """
                function MapCode() {
	emit(this.shortTeam1,
	{
		"score": this.pointsTeam1
	});
}
                """)

  def getMatchesByMatchday(self,matchday=getCurrentMatchday()):
    matches = bl_1.find({'groupOrderID':matchday}\
      ).sort([('groupOrderID',ASCENDING)])
    return matches
    
  def getMatchesByTeamName(self,teamName):
    matches = bl_1.find({'$or' : [{'nameTeam1':teamName},
      {'nameTeam2':teamName}]}).sort([('groupOrderID',ASCENDING)])
    return matches
    
  def getMatchesByTeamID(self,teamID):
    matches = bl_1.find({'$or' : [{'idTeam1':teamID},
      {'idTeam2':teamID}]}).sort([('groupOrderID',ASCENDING)])
    return matches
    
  def getMatchesByTeamShortcut(self,shortcut):
    matches = bl_1.find({'$or' : [{'shortTeam1':shortcut},
      {'shortTeam2':shortcut}]}).sort([('groupOrderID',ASCENDING)])
    return matches
    
  def getHomeMatchesByTeamID(self,teamID):
    matches = bl_1.find({'idTeam1':teamID}).sort([('groupOrderID',ASCENDING)])
    return matches
    
  def getAwayMatchesByTeamID(self,teamID):
    matches = bl_1.find({'idTeam2':teamID}).sort([('groupOrderID',ASCENDING)])
    return matches
    
  def getHomeMatchesByTeamName(self,teamName):
    matches = bl_1.find({'nameTeam1':teamName}\
      ).sort([('groupOrderID',ASCENDING)])
    return matches

  def getGoalsSinceGoalID(self,goalID):
    matches = bl_1.find({"goals.goalID": {"$gt": goalID}})
    # matches contains only those matches with goals above goalID
    matchgoals = {}
    for match in matches:
      newgoals = []
      for goal in match['goals']:
        tmp = {}
        if goal['goalID'] <= goalID: # get to the first goal with goalID > goalID
          continue
        else:
          idx = match['goals'].index(goal)
          if idx == 0: # first goal in the match
            if goal['goalScoreTeam1'] == 1: #team1 scored
              tmp['goalForTeamID'] = match['idTeam1']
              tmp['goalForTeamShortcut'] = match['shortTeam1']
              tmp['goalScorer'] = goal['goalGetterName']
              tmp['goalMatchMinute'] = goal['goalMatchMinute']
            else:
              tmp['goalForTeamID'] = match['idTeam2']
              tmp['goalForTeamShortcut'] = match['shortTeam2']
              tmp['goalScorer'] = goal['goalGetterName']
              tmp['goalMatchMinute'] = goal['goalMatchMinute']
          else: # not the first goal of the match
            if match['goals'][idx-1]['goalScoreTeam1'] < goal['goalScoreTeam1']:
              # team1 has scored
              tmp['goalForTeamID'] = match['idTeam1']
              tmp['goalForTeamShortcut'] = match['shortTeam1']
              tmp['goalScorer'] = goal['goalGetterName']
              tmp['goalMatchMinute'] = goal['goalMatchMinute']
            else: # team2 has scored
              tmp['goalForTeamID'] = match['idTeam2']
              tmp['goalForTeamShortcut'] = match['shortTeam2']
              tmp['goalScorer'] = goal['goalGetterName']
              tmp['goalMatchMinute'] = goal['goalMatchMinute']
          tmp['goalID'] = goal['goalID']
          tmp['goalPenalty'] = goal['goalPenalty']
          tmp['goalOwnGoal'] = goal['goalOwnGoal']
          tmp['goalComment'] = goal['goalComment']
          newgoals.append(tmp)
            
      matchgoals[match['matchID']] = newgoals
    return matchgoals
    
  def getMatchGoalsWithFlaggedUpdates(self,maxclientid):
    ''' @maxclientid: int representing highest goalID client device has
        This method returns a dictionary where the keys are the matchIDs and
        the value is a list of goals for that match with goals with goalID
        greater than maxclientid flagged as new.
    '''
    matches = bl_1.find({"goals.goalID": {"$gt": maxclientid}})
    # matches contains only those _matches_ with goals above goalID
    matchgoals = {}
    for match in matches:
      matchgoals[match['matchID']] =  []
      for goal in match['goals']:
        tmp = {}
        if goal['goalID'] > maxclientid:
          tmp['new'] = True
        else:
          tmp['new'] = False
        idx = match['goals'].index(goal)
        if idx == 0: # first goal in the match
          if goal['goalScoreTeam1'] == 1: #team1 scored
            tmp['goalForTeamID'] = match['idTeam1']
            tmp['goalForTeamShortcut'] = match['shortTeam1']
            tmp['goalScorer'] = goal['goalGetterName']
            tmp['goalMatchMinute'] = goal['goalMatchMinute']
          else:
            tmp['goalForTeamID'] = match['idTeam2']
            tmp['goalForTeamShortcut'] = match['shortTeam2']
            tmp['goalScorer'] = goal['goalGetterName']
            tmp['goalMatchMinute'] = goal['goalMatchMinute']
        else: # not the first goal of the match
          if match['goals'][idx-1]['goalScoreTeam1'] < goal['goalScoreTeam1']:
            # team1 has scored
            tmp['goalForTeamID'] = match['idTeam1']
            tmp['goalForTeamShortcut'] = match['shortTeam1']
            tmp['goalScorer'] = goal['goalGetterName']
            tmp['goalMatchMinute'] = goal['goalMatchMinute']
          else: # team2 has scored
            tmp['goalForTeamID'] = match['idTeam2']
            tmp['goalForTeamShortcut'] = match['shortTeam2']
            tmp['goalScorer'] = goal['goalGetterName']
            tmp['goalMatchMinute'] = goal['goalMatchMinute']
        tmp['goalID'] = goal['goalID']
        tmp['goalPenalty'] = goal['goalPenalty']
        tmp['goalOwnGoal'] = goal['goalOwnGoal']
        tmp['goalComment'] = goal['goalComment']
        matchgoals[match['matchID']].append(tmp)
    return matchgoals

    
  def getAwayMatchesByTeamName(self,teamName):
    matches = bl_1.find({'nameTeam2':teamName}\
      ).sort([('groupOrderID',ASCENDING)])
    return matches
  
  def getHomeMatchesByTeamShortcut(self,shortcut):
    matches = bl_1.find({'shortTeam1':shortcut}\
        ).sort([('groupOrderID',ASCENDING)])
    return matches
    
  def getAwayMatchesByTeamShortcut(self,shortcut):
    matches = bl_1.find({'shortTeam2':shortcut}\
        ).sort([('groupOrderID',ASCENDING)])
    return matches
    
  def getTableOnMatchday(self,matchday=getCurrentMatchday()):
    teamwin = bl_1.group(['pointsDiv'],
                        {'matchIsFinished':True},
                        {'list': []}, # initial
                        'function(obj, prev) {prev.list.push(obj)}')
    y = []
    for x in teamwin:
      y.append(x)
    return y


    for x in teamdraw:
      if len(x['onepoint']):
        for id in x['onepoint']:
          teamid = int(id)
          if not teams.has_key(teamid):
            teams[teamid] = {'points':0,'won':0,'lost':0,'drew':0,'gd':-0}
          d = teams[teamid]
          d['drew']+=1
          d['points']+=1
    return teams
        
    
  def getTableRelevantStatsByTeamID(self,teamID):
    matches = bl_1.find({'$or':[{'idTeam1':teamID},{'idTeam2':teamID}]})
    win,loss,draw,points = 0,0,0,0
    for match in matches:
      if not match['matchIsFinished']:
        continue
      if match['idTeam1'] == teamID:
        if match['pointsTeam1'] > match['pointsTeam2']:
          win+=1
          points+=3
        elif match['pointsTeam1'] == match['pointsTeam2']:
          draw+=1
          points+=1
        else:
          loss+=1
      else:
        if match['pointsTeam2'] > match['pointsTeam1']:
          win+=1
          points+=3
        elif match['pointsTeam2'] == match['pointsTeam1']:
          draw+=1
          points+=1
        else:
          loss+=1
    return (win,loss,draw,points)
    
  def getTeams(self,league=getDefaultLeague(),season=getCurrentSeason()):
    tdict = {}
    teams = bl_1.find({'leagueSaison':season,'leagueShortcut':league},
                  {'nameTeam1':1,'nameTeam2':1,'idTeam1':1,'idTeam2':1,
                  'shortTeam1':1
                         }).sort([('nameTeam1',ASCENDING)])
    for team in teams:
      if tdict.has_key(team['idTeam1']):
        pass
      else:
        tdict[team['idTeam1']] = {'teamName':team['nameTeam1'],
                                  'teamShortcut':team['shortTeam1']}
    return tdict
      
      
