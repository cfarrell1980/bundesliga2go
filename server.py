import web,json,re,os
from api import localService
from PermaData import DBASE
from datetime import datetime
from subprocess import Popen,PIPE
api = localService()
def SYNC():
  from sync import SyncAPI
  sync = SyncAPI()
  print "syncing leagues..."
  sync.syncLeagues()
  print "syncing teams..."
  sync.syncTeams()
  print "syncing season data..."
  sync.syncSeasonMatches()

# Check if the scheduler is running. If not, do not continue
procs = Popen(['ps', '-A', '-F'], stdout=PIPE).communicate()[0]
if not re.search('bundesligaScheduler.py',procs):
  raise StandardError,"bundesligaScheduler.py is not running. Start it first!"
else:
  print "bundesligaScheduler.py is already running. Good!"
  
# Sync the local database with upstream...
SYNC()

web.config.debug = True
urls = (
  '/api/match/(.*?)/?','jsonMatch',
  '/api/matchday/(\d{1,2})/?','jsonMatchday',
  '/api/team/(.*?)/?','jsonTeam',
  '/api/goal/(\d{1,6})/?','jsonGoal',
  '/api/matches/inprogress/(.*?)/?','jsonMatchesInProgess',
  '/api/teams','jsonTeams',
)
app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()

class jsonMatch:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "POST,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self,match=None):
    web.header('Content-Type','application/json')
    if not match:
      # api method getLastMatch
      return json.dumps("Foo")
    else:
      try:
        match = int(match)
      except ValueError:
        return json.dumps({'error':'match id must be type int'})
      else:
        try:
          match = api.getMatchByID(match)
        except:
          return json.dumps({'error':'no match with id %d'%match})
        else:
          return json.dumps(match)
          
class jsonTeam:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self,team=None):
    web.header('Content-Type','application/json')
    if not team:
      return json.dumps("Foo")
    else:
      try:
        team = int(team)
      except ValueError:
        try:
          team = api.getTeamByShortname(team)
        except:
          return json.dumps({'error':'no team with shortname %s'%team})
        else:
          return json.dumps(team)
      else:
        try:
          team = api.getTeamByID(team)
        except Exception,e:
          return json.dumps({'error':'no team with id %d'%team})
        else:
          return json.dumps(team)
      
class jsonGoal:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self,goal=None):
    web.header('Content-Type','application/json')
    if not goal:
      return json.dumps({'error':'no goal id provided'})
    else:
      try:
        goal = int(goal)
      except ValueError:
        return json.dumps({'error':'goal id must be type int'})
      else:
        try:
          goal = api.getGoalByID(goal)
        except:
          return json.dumps({'error':'no goal with id %d'%goal})
        else:
          return json.dumps(goal)
      
class jsonMatchesInProgess:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self,tstamp=None):
    web.header('Content-Type','application/json')
    if not tstamp:
      mip = api.getMatchesInProgressNow()
      return json.dumps(mip)
    else:
      try:
        tstamp = datetime.strptime(tstamp,"%Y-%m-%d-%H-%M")
      except:
        return json.dumps({'error':'%s is an invalid tstamp.'%tstamp})
      else:
        mip = api.getMatchesInProgressAsOf(tstamp)
        return json.dumps(mip)
        
class jsonTeams:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self):
    web.header('Content-Type','application/json')
    teams = api.getTeams()
    return json.dumps(teams)
    
    
if __name__ == '__main__':
  app.run()
