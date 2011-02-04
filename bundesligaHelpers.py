
'''
Copyright (c) 2011, Ciaran Farrell, Vladislav Gorobets
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

from datetime import datetime
from OpenLigaDB import OpenLigaDB
import hashlib,json,os,sys

if os.environ.has_key('TMPDIR'):
  LocalStorage = os.path.join(os.environ['TMPDIR'],'bundesligaMobile')
else:
  LocalStorage = "/tmp/bundesligaMobile"

# mobile screens not wide enough to display full club names
shortcuts = {40: 'FCB',9:'S04',134:'BRE',6:'B04',16:'FVB',7:'BVB',
             131:'WOB',87:'BMG',76:'FCK',112:'SCF',81:'MO5',91:'FFM',
             65:'1FCK',98:'FCP',123:'HOF',79:'1FCN',55:'H96',100:'HSV',
             54:'BSC',129:'BOC',105:'KSC',83:'DSC',93:'FCE',125:'M60',
             185:'F95',23:'AAC',107:'MSV',95:'FCA',173:'RWO',80:'FCU',
             66:'AUE',36:'OSN',115:'SGF',31:'SCP',171:'FCI',172:'FSV',
             29:'OFF',69:'CZJ',127:'TUK',174:'SWW',102:'ROS'
            }

def json_serialize(obj):
  try:
    return obj.__dict__
  except:
    #raise TypeError(repr(obj)+" is not JSON serializable")
    return str(obj)

def current_bundesliga_season():
  ''' openligadb declares the year for any bundesliga season to be the
      year in which the season started. Therefore, even if we currently
      have February 2011, the year/season will be defined as 2010
      because that season started in 2010. Accordingly, this function
      simply checks the current year and returns it if we are in the 
      period August to December. If we are in the period January to
      July the function returns current year - 1 '''
  now = datetime.now()
  current_year = now.year
  current_month = now.month
  if current_month < 8:
    return int(current_year-1)
  else:
    return int(current_year)

def checksum(thefile):
  md5 = hashlib.md5()
  with open('%s'%thefile,'rb') as f:
    for chunk in iter(lambda: f.read(8192), ''):
      md5.update(chunk)
  return str(md5.hexdigest()).encode('utf-8')

def tstamp_to_md5(tstamp):
  '''Converts the timestamp we get back from OpenLigaDB to md5.
     This md5 value is sent to the mobile client. Every request
     from the mobile client is thereafter checked for the md5.
     The client md5 can be compared with the updated OpelLigaDB
     md5 to determine if the client's data cache is up to date
  '''
  md5 = hashlib.md5()
  md5.update(tstamp.strftime("%Y%m%d%H%M%s"))
  return md5.hexdigest()

def matchdataBymatchday(soapobj):
  '''Return season data sorted by matchday'''
  returnDict = {}
  for match in soapobj.Matchdata:
    container = {}
    for key in match: #match is a tuple
      k,v = key[0],key[1]#k is the key, v can be str,list,instance etc
      if k == 'matchID':
        container['matchID'] = v
      elif k == 'nameTeam1':
        container['nameTeam1'] = v.encode('utf-8')
      elif k == 'nameTeam2':
        container['nameTeam2'] = v.encode('utf-8')
      elif k == 'pointsTeam1':
        container['pointsTeam1'] = int(v)
      elif k == 'pointsTeam2':
        container['pointsTeam2'] = int(v)
      elif k == 'iconUrlTeam1':
        if v:
          container['iconUrlTeam1'] = v.encode('utf-8')
        else:
          container['iconUrlTeam1'] = None
      elif k == 'iconUrlTeam2':
        if v:
          container['iconUrlTeam2'] = v.decode('utf-8')
        else:
          container['iconUrlTeam2'] = None
      elif k == 'matchIsFinished':
        container['matchIsFinished'] = v
      elif k == 'groupOrderID':
        container['groupOrderID'] = int(v)
      elif k == 'leagueName':
        container['leagueName'] = v.encode('utf-8')
      elif k == 'leagueShortcut':
        container['leagueShortcut'] = v.encode('utf-8')
      elif k == 'matchDateTime':
        container['matchDateTime'] = v.isoformat()
      elif k == 'idTeam1':
        container['idTeam1'] = int(v)
        if shortcuts.has_key(int(v)):
          container['shortTeam1'] = shortcuts[int(v)]
        else:
          container['shortTeam1'] = None
      elif k == 'idTeam2':
        container['idTeam2'] = int(v)
        if shortcuts.has_key(int(v)):
          container['shortTeam2'] = shortcuts[int(v)]
        else:
          container['shortTeam2'] = None
      elif k == 'lastUpdate':
        last_update_md5 = tstamp_to_md5(v)
        container['lastUpdate'] = v.isoformat()
        container['md5'] = last_update_md5
      elif k == 'goals':
        goals = []
        if hasattr(v,'Goal'):
          for goalobj in v.Goal:
            gdict = {}
            if hasattr(goalobj,'goalGetterName'):
              gdict['goalGetterName'] = goalobj.goalGetterName.encode('utf-8')
            else:
              gdict['goalGetterName'] = None
            gdict['goalID'] = goalobj.goalID
            gdict['goalScoreTeam1'] =  goalobj.goalScoreTeam1
            gdict['goalScoreTeam2'] = goalobj.goalScoreTeam2
            gdict['goalMatchMinute'] = goalobj.goalMatchMinute
            gdict['goalGetterID'] = goalobj.goalGetterID
            gdict['goalPenalty'] =  goalobj.goalPenalty
            gdict['goalOwnGoal'] = goalobj.goalOwnGoal
            gdict['goalOvertime'] = goalobj.goalOvertime
            goals.append(gdict)
        container['goals'] = goals
    if returnDict.has_key(container['groupOrderID']):
      returnDict[container['groupOrderID']][container['matchID']] = container
    else:
      returnDict[container['groupOrderID']] = {container['matchID']:container}
  return returnDict

def saveSeasonData(dataobj,where):
  fd = open(where,'w')
  json.dump(dataobj,fd)
  fd.close()
  return True

def fakeSeasonData(league,season):
  fd = open('/tmp/bundesligaMobile/2010/bl1.json','r')
  bdict = json.load(fd)
  fd.close()
  return bdict

def bootstrapLocalStorage(league,season):
  season_dir = os.path.join(LocalStorage,"%s/%s"%(season,league))
  if not os.path.isdir(season_dir):
    sys.stdout.write("Season directory %s does not exist...creating\n"%season_dir)
    try:
      os.makedirs(season_dir)
    except Exception,e:
      print "Could not create storage directory for season %s at %s: %s\n"%(season,season_dir,str(e))
      raise
    else:
      sys.stdout.write("Successfully created storage directory for season %s at %s\n"%(season,season_dir))
  else:
    sys.stdout.write("Directory for season %s already exists at %s...using\n"%(season,season_dir))

def getGoalsByMatchID(matchID):
  '''Return a JSON object containing goal information for a given matchID. This
     function currently returns the data directly from openligadb.de.
     TODO: Find a way of caching this locally. Using the existing season based 
     data cache is not ideal because of how the data there is stored
  '''
  cursor = OpenLigaDB()
  goals = cursor.GetGoalsByMatch(matchID)
  goalList = []
  try:
    for goal in goals.Goal:
      goaldict = {}
      goaldict['goalID'] = goal.goalID
      goaldict['goalMatchID'] = goal.goalMachID
      goaldict['goalScoreTeam1'] = goal.goalScoreTeam1
      goaldict['goalScoreTeam2'] = goal.goalScoreTeam2
      goaldict['goalMatchMinute'] = goal.goalMatchMinute
      #goaldict['goalGetterID'] = goal.goalGetterID
      goaldict['goalGetterName'] = goal.goalGetterName.encode('utf-8')
      goaldict['goalPenalty'] = goal.goalPenalty
      #goaldict['goalOwnGoal'] = goal.goalOwnGoal #ignore as it's often wrong
      #goaldict['goalOvertime'] = goal.goalOvertime
      goalList.append(goaldict)
  except AttributeError:
    raise StandardError, "No data exists for matchID %s"%str(matchID)
  else:
    return goalList

def getSeasonData(league,season):
  cursor = OpenLigaDB()
  try:
    bootstrapLocalStorage(league,season)
  except Exception, e:
    raise StandardError, "Could not bootstrap LocalStorage: %s"%str(e)
  else:
    sys.stdout.write("LocalStorage bootstrapped for %s %s\n"%(league,season))

  jsonfile = os.path.join(LocalStorage,"%s/%s.json"%(season,league))
  upstream_tstamp = cursor.GetLastChangeDateByLeagueSaison(league,season)
  md5 = tstamp_to_md5(upstream_tstamp)

  if os.path.isfile(jsonfile):
    fd = open(jsonfile,'r')
    data = json.load(fd)
    fd.close()
    if data.has_key('seasonMD5'):
      local_tstamp = data['seasonMD5']
    else:
      return updateLocalStorage(league,season,jsonfile)
    if local_tstamp != md5:
      print "update required from openligadb.de"
      return updateLocalStorage(league,season,jsonfile)
    else:
      print "no update required => returning local data"
      return data
  else:
    print "no JSON file available for %s %s - update required"%(league,season)
    return updateLocalStorage(league,season,jsonfile)

def updateLocalStorage(league,season,jsonfile):
  cursor = OpenLigaDB()
  remote_data = cursor.GetMatchdataByLeagueSaison(league,season)
  upstream_tstamp = cursor.GetLastChangeDateByLeagueSaison(league,season)
  md5 = tstamp_to_md5(upstream_tstamp)
  pyobj = matchdataBymatchday(remote_data)
  pyobj['seasonMD5'] = md5
  fd = open(jsonfile,'w')
  json.dump(pyobj,fd)
  fd.close()
  fd = open(jsonfile,'r')
  data = json.load(fd)
  fd.close()
  return data


def updateMatchById(matchID):
  '''Given a matchID download only the goal info about the match and other time
     specific information such as the matchIsFinished boolean'''
  pass
    

