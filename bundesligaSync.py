from OpenLigaDB import OpenLigaDB
from pymongo import Connection,ASCENDING
from datetime import datetime
from bundesligaGlobals import *
connection = Connection()
db = connection.bundesliga2go
bl_1 = db.bl1_2011
bl_1.ensure_index([('teamName1',ASCENDING),
                  ('teamName2',ASCENDING),
                  ('leagueName',ASCENDING),
                  ('leagueSaison',ASCENDING),
                  ('goals.goalGetterName',ASCENDING)])
oldb = OpenLigaDB(timeout=14)

    
def goalToDict(goal):
  g = {}
  g['goalID'] = goal.goalID
  g['goalMatchID'] = goal.goalMachID # is this really broken upstream (typo)?
  g['goalScoreTeam1'] = goal.goalScoreTeam1
  g['goalScoreTeam2'] = goal.goalScoreTeam2
  g['goalMatchMinute'] = goal.goalMatchMinute
  g['goalGetterID'] = goal.goalGetterID
  g['goalGetterName'] = goal.goalGetterName
  g['goalPenalty'] = goal.goalPenalty
  g['goalOwnGoal'] = goal.goalOwnGoal
  g['goalOvertime'] = goal.goalOvertime
  if hasattr(goal,'goalComment'):
    g['goalComment'] = goal.goalComment
  else:
    g['goalComment'] = None
  return g
    
def matchToDict(match):
  m = {}
  m['matchID'] = match.matchID
  m['matchDateTime'] = match.matchDateTime
  m['TimeZoneID'] = match.TimeZoneID
  m['matchDateTimeUTC'] = match.matchDateTimeUTC
  m['groupID'] = match.groupID
  m['groupOrderID']= match.groupOrderID
  m['groupName'] = match.groupName
  m['leagueID'] = match.leagueID
  m['leagueName'] = match.leagueName
  m['leagueSaison'] = int(match.leagueSaison)
  m['leagueShortcut'] = match.leagueShortcut
  m['nameTeam1'] = match.nameTeam1
  m['nameTeam2'] = match.nameTeam2
  m['idTeam1'] = match.idTeam1
  m['idTeam2'] = match.idTeam2
  m['shortTeam1'] = getTeamShortcut(match.idTeam1)
  m['shortTeam2'] = getTeamShortcut(match.idTeam2)
  m['iconUrlTeam1'] = match.iconUrlTeam1
  m['iconUrlTeam2'] = match.iconUrlTeam2
  m['pointsTeam1'] = match.pointsTeam1
  m['pointsTeam2'] = match.pointsTeam2
  m['lastUpdate'] = match.lastUpdate
  m['matchIsFinished'] = match.matchIsFinished
  m['NumberOfViewers'] = match.NumberOfViewers
  if hasattr(match.location,'locationCity'):
    m['locationCity'] = match.location.locationCity
  else: m['locationCity'] = None
  if hasattr(match.location,'locationStadium'):
    m['locationStadium'] = match.location.locationStadium
  else: m['locationStadium'] = None
  m['goals'] = []
  if hasattr(match.goals,'Goal'):
    for g in match.goals.Goal:
      m['goals'].append(goalToDict(g))
      
  if hasattr(match.matchResults,'matchResult'):
    for entry in match.matchResults.matchResult:
      if entry.resultName == 'Endergebnis':
        m['Endergebnis'] = {  'pointsTeam1':entry.pointsTeam1,
                              'pointsTeam2':entry.pointsTeam2
                           }
      if entry.resultName == 'Halbzeit':
        m['Halbzeit'] = { 'pointsTeam1':entry.pointsTeam1,
                          'pointsTeam2':entry.pointsTeam2
                        }
  else:
    m['Endergebnis'] = {}
    m['Halbzeit'] = {}
  return m

class bundesligaSync:

  def dropLocal(self):
    db.drop_collection("bl1_2011")
    
  def matchesToMongo(self,league=getDefaultLeague(),
                       season=getCurrentSeason()):
    md = oldb.GetMatchdataByLeagueSaison(league,season)
    matchdata = md.Matchdata
    for x in matchdata:
      mdict = matchToDict(x)
      existing_match = bl_1.find_one({'matchID':mdict['matchID']})
      if existing_match:
        print "matchID %d exists. Updating..."%mdict['matchID']
        bl_1.update({'matchID':mdict['matchID']},
            {'$set':{ 'matchIsFinished':mdict['matchIsFinished'],
                      'pointsTeam1':mdict['pointsTeam1'],
                      'pointsTeam2':mdict['pointsTeam2'],
                      'lastUpdate':mdict['lastUpdate'],
                      'NumberOfViewers':mdict['NumberOfViewers'],
                      'locationCity':mdict['locationCity'],
                      'locationStadium':mdict['locationStadium'],
                      'goals':mdict['goals']
                      }},upsert=True)
      else:
        print "matchID %d does not exist. Inserting..."%mdict['matchID']
        bl_1.insert(mdict)
    
  def matchToMongo(self,matchID):
    md = oldb.GetMatchByMatchID(matchID)
    mdict = matchToDict(md)
    existing_match = bl_1.find_one({'matchID':mdict['matchID']})
    if existing_match:
      print "matchID %d exists. Updating..."%mdict['matchID']
      bl_1.update({'matchID':mdict['matchID']},
          {'$set':{ 'matchIsFinished':mdict['matchIsFinished'],
                    'pointsTeam1':mdict['pointsTeam1'],
                    'pointsTeam2':mdict['pointsTeam2'],
                    'lastUpdate':mdict['lastUpdate'],
                    'NumberOfViewers':mdict['NumberOfViewers'],
                    'locationCity':mdict['locationCity'],
                    'locationStadium':mdict['locationStadium'],
                    'goals':mdict['goals']
                    }},upsert=True)
    else:
      print "matchID %d does not exist. Inserting..."%mdict['matchID']
      bl_1.insert(mdict)

if __name__ == '__main__':
  syncer = bundesligaSync()
  syncer.matchesToMongo()
