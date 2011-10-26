from pymongo import Connection,ASCENDING,DESCENDING
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
                
  def jsonifyMatch(self,match,allkeys=False):
    match['lastUpdate'] = match['lastUpdate'].strftime("%Y-%m-%d %H:%M")
    match['matchDateTime'] = match['matchDateTime'].strftime("%Y-%m-%d %H:%M")
    match['matchDateTimeUTC'] = match['matchDateTimeUTC'].strftime("%Y-%m-%d %H:%M")
    match['_id'] = None
    goals_dict = {}
    for goal in match['goals']:
      tmp = {}
      idx = match['goals'].index(goal)
      if idx == 0: # first goal in the match
        if goal['goalScoreTeam1'] == 1: #team1 scored
          tmp['goalForTeamID'] = match['idTeam1']
        else:
          tmp['goalForTeamID'] = match['idTeam2']
      else: # not the first goal of the match
        if match['goals'][idx-1]['goalScoreTeam1'] < goal['goalScoreTeam1']:
          # team1 has scored
          tmp['goalForTeamID'] = match['idTeam1']
        else: # team2 has scored
          tmp['goalForTeamID'] = match['idTeam2']
      tmp['goalForTeamShortcut'] = match['shortTeam2']
      tmp['goalScorer'] = goal['goalGetterName']
      tmp['goalMatchMinute'] = goal['goalMatchMinute']
      tmp['goalID'] = goal['goalID']
      tmp['goalPenalty'] = goal['goalPenalty']
      tmp['goalOwnGoal'] = goal['goalOwnGoal']
      tmp['goalGetterName'] = goal['goalGetterName']
      #tmp['goalScoreTeam1'] = goal['goalScoreTeam1']
      #tmp['goalScoreTeam2'] = goal['goalScoreTeam2']
      if not goals_dict.has_key(tmp['goalForTeamID']):
        goals_dict[tmp['goalForTeamID']] = []
      goals_dict[tmp['goalForTeamID']].append(tmp)
    match['goals'] = goals_dict
    if not allkeys:
      del match['lastUpdate']
      del match['locationStadium']
      del match['Endergebnis']
      del match['Halbzeit']
      del match['iconUrlTeam1']
      del match['iconUrlTeam2']
      del match['NumberOfViewers']
      del match['TimeZoneID']
      del match['matchDateTimeUTC']
      del match['_id']
      del match['locationCity']
      del match['leagueID']
      del match['leagueShortcut']
    return match

  def getMatchesByMatchday(self,matchday=None,allkeys=False):
    if not matchday:
      matchday = getCurrentMatchday()
    matches = bl_1.find({'groupOrderID':matchday}\
      ).sort([('groupOrderID',ASCENDING)])
    retlist = []
    for x in matches:
      jsonMatch = self.jsonifyMatch(x,allkeys=allkeys)
      retlist.append(jsonMatch)
    print retlist
    return retlist
        
  def getMatchByID(self,id):
    match = bl_1.find_one({'matchID':id})
    print match
    if not match:
      raise StandardError, 'no match with matchID %d'%id
    else:
      return self.jsonifyMatch(match)
         
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
    
  def getMatchesUpcoming(self,league=None,season=None,limit=None):
    if not limit: limit = 20
    matches = bl_1.find({'matchDateTime':{'$gt':datetime.now()}},
                        sort=[('matchDateTime',ASCENDING)])[:limit]
    m = []
    for match in matches:
      m.append(self.jsonifyMatch(match))
    return m
  
  def getGoalByID(self,goalID):
    # TODO: there has to be a better way of doing this
    goals = bl_1.find({},{'goals':1})
    for goal in goals:
      for x in goal['goals']:        
        if x['goalID'] == goalID:
          return x
    
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
    
  def getMatchGoalsWithFlaggedUpdates(self,maxclientid,
    league=None):
    ''' @maxclientid: int representing highest goalID client device has
        This method returns a dictionary where the keys are the matchIDs and
        the value is a list of goals for that match with goals with goalID
        greater than maxclientid flagged as new.
    '''
    if not league:
      league = getDefaultLeague()
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
    
  def getTopScorers(self,matchday=None,limit=None,
    sortdir='DESC',league=None,onlyFinished=True):
    if not matchday:
      matchday = getCurrentMatchday()
    if not league:
      league = getDefaultLeague()
    m = Code('''function () {
      if(!this.goals){
        return;
      }
      for (var idx in this.goals){
        //if(this.goals[idx].goalPenalty == true){
         // emit(this.goals[idx]['goalGetterName'],[1,1]);
        //}
        //else{
          emit(this.goals[idx]['goalGetterName'],1);
        //}
      }
    }
    ''')
    r = Code('''function (k,v){
      var goals = 0;
      //var penalties = 0;
      for (i in v){
        goals+=v[i];
        //penalties+=v[i][1];
      }
      return goals;
    }
    ''')
    result = bl_1.map_reduce(m, r, out="foo",query={
        'groupOrderID':{'$lte':matchday}})
    scorerlist = []
    if sortdir=='DESC':
      sd = DESCENDING
    else:
      sd = ASCENDING
    for doc in result.find({},sort=[('value',sd)]):
      scorerlist.append(doc)
    if limit:
      if len(scorerlist) > limit:
        return scorerlist[:limit]
      elif len(scorerlist) == limit:
        return scorerlist[:limit-1]
    return scorerlist
        
            
  def getTableOnMatchday(self,matchday=None):
    if not matchday:
      matchday=getCurrentMatchday()
    m = Code('''function() {
     var tablePoints1 = 0;
     var tablePoints2 = 0;
     if (this.pointsTeam1 == this.pointsTeam2) {
       tablePoints1 = 1;
       tablePoints2 = 1;
     }
     else {
       if (this.pointsTeam1 > this.pointsTeam2) {
         tablePoints1 = 3;
       }
       else {
         tablePoints2 = 3;
       }
     }
     emit(this.idTeam1, [tablePoints1, this.pointsTeam1, this.pointsTeam2]);
     emit(this.idTeam2, [tablePoints2, this.pointsTeam2, this.pointsTeam1]);
    }''')
    r = Code("""function(k,values) { 
       var points = 0;
       var goalsfor = 0;
       var goalsagainst = 0;
       var goaldiff = 0;
       var won = 0;
       var lost = 0;
       var drew = 0;
       var played = 0;
       for (var i in values){
        if(values[i][0]==3){
          won+=1;
        }
        else if(values[i][0]==1){
          drew+=1;
        }
        else {
          lost+=1
        }
        points+=values[i][0];
        goalsfor+=values[i][1];
        goalsagainst+=values[i][2];
       }
       goaldiff = goalsfor-goalsagainst;
       played = won+lost+drew;
       return {points:points,played:played,goalsfor:goalsfor,goalsagainst:goalsagainst,goaldiff:goaldiff,won:won,lost:lost,drew:drew};
    }""")
    tablelist = []
    result = bl_1.map_reduce(m, r, out="foo",query={'matchIsFinished':True})
    for teamresults in result.find(sort=[('value.points',DESCENDING),
              ('value.goaldiff',DESCENDING)]):
      t,v = teamresults['_id'],teamresults['value']
      tmp = {'id':t,'won':v['won'],'lost':v['lost'],'played':v['played'],
             'drew':v['drew'],'points':v['points'],'goaldiff':v['goaldiff'],
             'goalsagainst':v['goalsagainst'],'goalsfor':v['goalsfor']}
      tablelist.append(tmp)
    return tablelist
    
        
    
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
    
  def getTeams(self,league=None,season=None,
                withurl=False):
    if not league:
      league = getDefaultLeague()
    if not season:
      season = getCurrentSeason()
    tdict = {}
    teams = bl_1.find({'leagueSaison':season,'leagueShortcut':league},
                  {'nameTeam1':1,'nameTeam2':1,'idTeam1':1,'idTeam2':1,
                  'shortTeam1':1,'iconUrlTeam1':1,'iconUrlTeam2':1
                         }).sort([('nameTeam1',ASCENDING)])
    for team in teams:
      if tdict.has_key(team['idTeam1']):
        pass
      else:
        tdict[team['idTeam1']] = {'teamName':team['nameTeam1'],
                                  'teamShortcut':team['shortTeam1']}
        if withurl:
          tdict[team['idTeam1']]['iconURL'] = team['iconUrlTeam1']
    return tdict
    
  def getTeamByID(self,id):
    t = bl_1.find_one({'idTeam1':id})
    if not t:
      raise StandardError, 'no team with id %d'%id
    else:
      return {'id':t['idTeam1'],'name':t['nameTeam1'],
        'shortcut':t['shortTeam1']}
    
  def getTeamByShortcut(self,shortcut):
    t = bl_1.find_one({'shortTeam1':shortcut})
    if not t:
      raise StandardError, 'no team with shortcut %s'%shortcut
    else:
      return {'id':t['idTeam1'],'name':t['nameTeam1'],
        'shortcut':t['shortTeam1']}
        
  def getMaxGoalID(self,league=None):
    if not league:
      league = getDefaultLeague()
    # This is horrible hackery. TODO: use map reduce?
    goals = bl_1.find({"goals.goalID": {"$gt": 0}},{'goals.goalID':1}
            )
    goallist = []
    for goald in goals:
      g = goald['goals']
      for gdict in g:
        goallist.append(gdict['goalID'])
    goallist.sort()
    return goallist[-1]
    
  def getMatchesInProgress(self,when=None,league=None,
      season=None,ids_only=False):
    if not league:
      league = getDefaultLeague()
    if not season:
      season = getCurrentSeason()
    mlist = []
    if not when:
      when = datetime.now()
    if ids_only:
      matches = bl_1.find({'matchDateTime':{'$lte':when},
                          'matchIsFinished':False},{'matchID':1})

    else:
      matches = bl_1.find({'matchDateTime':{'$lte':when},
                          'matchIsFinished':False})
    for x in matches:
      # extra check needed as OpenLigaDB forgets to set match.IsFinished sometimes
      if x['matchDateTime'].strftime("%Y-%m-%d") == datetime.now().strftime("%Y-%m-%d"):
        if ids_only:
          mlist.append(x['matchID'])
        else:
          mlist.append(self.jsonifyMatch(x))
    return mlist
