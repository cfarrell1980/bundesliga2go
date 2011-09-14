from pymongo import Connection,ASCENDING
from datetime import datetime
from bundesligaGlobals import *
connection = Connection()
db = connection.bundesliga2go
bl_1 = db.bl1_2011

class bundesligaAPI:

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
    
  def getTeams(self,league=getDefaultLeague(),season=getCurrentSeason()):
    # need a map reduce here
    tdict = {}
    teams = bl_1.find({},{'nameTeam1':1,'nameTeam2':1,'idTeam1':1,'idTeam2':1,
                         }).sort([('nameTeam1',ASCENDING)])
    for team in teams:
      if tdict.has_key(team['idTeam1']):
        pass
      else:
        tdict[team['idTeam1']] = {'teamName':team['nameTeam1']}
    return tdict
      
      
