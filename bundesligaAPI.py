from pymongo import Connection
from datetime import datetime
from bundesligaGlobals import *
connection = Connection()
db = connection.bundesliga2go
bl_1 = db.bl1_2011

class bundesligaAPI:
  def getMatchesByMatchday(self,matchday=getCurrentMatchday()):
    matches = bl_1.find({'groupOrderID':matchday}\
      ).sort(('groupOrderID',ASCENDING))
    return matches
    
  def getMatchesByTeamName(self,teamName):
    matches = bl_1.find({'$or' : [{'nameTeam1':teamName},
      {'nameTeam2':teamName}]}).sort(('groupOrderID',ASCENDING))
    return matches
    
  def getMatchesByTeamID(self,teamID):
    matches = bl_1.find({'$or' : [{'idTeam1':teamID},
      {'idTeam2':teamID}]}).sort(('groupOrderID',ASCENDING))
    return matches
    
  def getMatchesByTeamShortcut(self,shortcut):
    matches = bl_1.find({'$or' : [{'shortTeam1':shortcut},
      {'shortTeam2':shortcut}]}).sort(('groupOrderID',ASCENDING))
    return matches
    
  def getHomeMatchesByTeamID(self,teamID):
    matches = bl_1.find({'idTeam1':teamID}).sort(('groupOrderID',ASCENDING))
    return matches
    
  def getAwayMatchesByTeamID(self,teamID):
    matches = bl_1.find({'idTeam2':teamID}).sort(('groupOrderID',ASCENDING))
    return matches
    
  def getHomeMatchesByTeamName(self,teamName):
    matches = bl_1.find({'nameTeam1':teamName}).sort(('groupOrderID',ASCENDING))
    return matches
    
  def getAwayMatchesByTeamName(self,teamName):
    matches = bl_1.find({'nameTeam2':teamName}).sort(('groupOrderID',ASCENDING))
    return matches
  
  def getHomeMatchesByTeamShortcut(self,shortcut):
    matches = bl_1.find({'shortTeam1':shortcut}\
        ).sort(('groupOrderID',ASCENDING))
    return matches
    
  def getAwayMatchesByTeamShortcut(self,shortcut):
    matches = bl_1.find({'shortTeam2':shortcut}\
        ).sort(('groupOrderID',ASCENDING))
    return matches
    
  def getTeams(self,league=getDefaultLeague(),season=getCurrentSeason()):
    # need a map reduce here
    tdict = {}
    teams = bl_1.find({},{'nameTeam1':1,'nameTeam2':1,'idTeam1':1,'idTeam2':1,
                         }).sort(('nameTeam1',ASCENDING))
    for team in teams:
      if tdict.has_key(team['idTeam1']):
        pass
      else:
        tdict[team['idTeam1']] = {'teamName':team['nameTeam1']}
    return tdict
      
      
