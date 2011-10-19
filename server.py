#!/usr/bin/python
"""A web.py application powered by gevent"""
from bundesligaAPI import bundesligaAPI
from bundesligaSync import *
#from gevent import monkey; monkey.patch_all()
#from gevent.pywsgi import WSGIServer
import gevent,web,json,os,sys
api = bundesligaAPI()

urls = (
  '/','index',
  '/long','long_polling',
  '/api/match/(.*?)/?','jsonMatch',
  '/api/matchday/(\d{1,2})/?','jsonMatchday',
  '/api/team/(.*?)/?','jsonTeam',
  '/api/goal/(\d{1,6})/?','jsonGoal',
  '/api/matches/inprogress/(.*?)/?','jsonMatchesInProgess',
  '/api/matches/upcoming/?','jsonMatchesUpcoming',
  '/api/teams/?','jsonTeams',
  '/api/goalssince/(\d{1,6})/?','jsonGoalsSince',
  '/api/maxgoalid','jsonMaxGoalID',
  '/api/table','getTableOnMatchday',
  '/api/topscorers','getTopScorers',
  '/api/routes','routes',
  '/ws','websocket',
)
class index:
  def GET(self):
    raise web.seeother('/static/foo.html')


class routes:
  def GET(self):
    d = {}
    for url in urls:
      print url
    return json.dumps(d)

class long_polling:
  # Since gevent's WSGIServer executes each incoming connection in a separate greenlet
  # long running requests such as this one don't block one another;
  # and thanks to "monkey.patch_all()" statement at the top, thread-local storage used by web.ctx
  # becomes greenlet-local storage thus making requests isolated as they should be.
  def GET(self):
    print 'GET /long'
    gevent.sleep(10)  # possible to block the request indefinitely, without harming others
    return 'Hello, 10 seconds later'
    
class getTeams:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self):
    web.header("Access-Control-Allow-Origin", "*")
    web.header('Content-Type','application/json')
    league = web.input(league=None).league
    season = web.input(season=None).season
    if not league:
      league = getDefaultLeague()
    if not season:
      season = getCurrentSeason()
    else:
      if not isinstance(season,int):
        try:
          season = int(season)
        except ValueError:
          return json.dumps({'error':'season must be int, not %s'%season})
    teams = api.getTeams(league,season)
    return json.dumps(teams)
    


class getNewGoals:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self):
    web.header("Access-Control-Allow-Origin", "*")
    web.header('Content-Type','application/json')
    clientmaxid = web.input(maxid=None).maxid
    if not clientmaxid:
      return json.dumps({'error':'maxid is a required parameter'})
    else:
      try:
        maxid = int(clientmaxid)
      except ValueError:
        return json.dumps({'error':'maxid must be an integer'})
    matches = api.getMatchGoalsWithFlaggedUpdates(maxid)
    return json.dumps(matches)

class getTableOnMatchday:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self):
    web.header("Access-Control-Allow-Origin", "*")
    web.header('Content-Type','application/json')
    matchday = web.input(matchday=None).matchday
    league = web.input(league=None).league
    if not league:
      league = getDefaultLeague()
    if not matchday:
      matchday = getCurrentMatchday()
    else:
      try:
        matchday = int(matchday)
      except ValueError:
        return json.dumps({'error':'matchday must be an integer'})
      else:
        if matchday < 1 or matchday > 34: # is this accurate?
          return json.dumps({'error':'matchday must be between 1 and 34'})
    if matchday == getCurrentMatchday():
      t = os.path.join('%s/cache/table.json'%getAppRoot())
      if os.path.exists(t):
        print "returning table from file"
        fd = open(t,'r').read()
        return fd
    print "returning table from fly"
    table = api.getTableOnMatchday(matchday)
    return json.dumps(table)

class getTopScorers:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self):
    web.header("Access-Control-Allow-Origin", "*")
    web.header('Content-Type','application/json')
    matchday = web.input(matchday=None).matchday
    limit = web.input(limit=None).limit
    sortdir=web.input(sortdir=None).sortdir
    if sortdir:
      if sortdir.upper() != 'ASC' and sortdir.upper() != 'DESC':
        return json.dumps({'error':'sortdir must be either ASC or DESC'})
      else:
        sortdir = 'DESC'
    else:
      sortdir = 'DESC'
    if limit:
      try:
        limit = int(limit)
      except ValueError:
        return json.dumps({'error':'limit must be an integer'})
      else:
        if limit < 1 or limit > 50:
          return json.dumps({'error':'limit must be between 1 and 50'})
    league = web.input(league=None)
    if not league:
      league = getDefaultLeague()
    if not matchday:
      matchday = getCurrentMatchday()
    else:
      try:
        matchday = int(matchday)
      except ValueError:
        return json.dumps({'error':'matchday must be an integer'})
      else:
        if matchday < 1 or matchday > 34: # is this accurate?
          return json.dumps({'error':'matchday must be between 1 and 34'})
    topscorers = api.getTopScorers(matchday=matchday,limit=limit,
        league=league,sortdir=sortdir)
    return json.dumps(topscorers)

class jsonGoal:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self,goal=None):
    web.header("Access-Control-Allow-Origin", "*")
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

class jsonTeam:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self,team=None):
    web.header("Access-Control-Allow-Origin", "*")
    web.header('Content-Type','application/json')
    if not team:
      return json.dumps({'error':'no team id or shortcut sent'})
    try:
      t = int(team)
    except ValueError:
      try:
        team = api.getTeamByShortcut(team.upper())
      except Exception,e:
        print e
        return json.dumps({'error':'no team with shortcut %s'%team})
      else:
        return json.dumps(team)
    else:
      try:
        team = api.getTeamByID(t)
      except Exception,e:
        print e
        return json.dumps({'error':'no team with id %d'%t})
      else:
        return json.dumps(team)
        
        
class jsonMatchesInProgess:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self,tstamp=None):
    web.header("Access-Control-Allow-Origin", "*")
    web.header('Content-Type','application/json')
    league = web.input(league=None).league
    season = web.input(season=None).season
    ids_only = web.input(ids_only=None).ids_only
    if not ids_only:
      ids_only = False
    else:
      ids_only = True
    if not league:
      league = getDefaultLeague()
    if not season:
      season = getCurrentSeason()
    try:
      tstamp = datetime.strptime(tstamp,"%Y-%m-%d-%H-%M")
    except:
      if not tstamp:
        mip = api.getMatchesInProgress(ids_only=ids_only)
        return json.dumps(mip)
      else:
        return json.dumps({'error':'bad tstamp'})
    else:
      mip = api.getMatchesInProgress(when=tstamp,ids_only=ids_only)
      return json.dumps(mip)
        
      
class jsonLeagueTable:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self):
    web.header("Access-Control-Allow-Origin", "*")
    web.header('Content-Type','application/json')
    season = web.input(season=None).season
    league = web.input(league=None).league
    matchday = web.input(matchday=None).matchday
    pointslist = []
    if not league:
      league = getDefaultLeague()
    if not season:
      season = getCurrentSeason()
    if not matchday:
      matchday = getCurrentMatchDay()
    try:
      teams = api.getTeams(league=league,season=season,ret_dict=False)
    except:
      return json.dumps({'error':'could not return team data'})
    else:
      for team in teams:
        ppt = api.getPointsPerTeam(team.id)
        pointslist.append(ppt)
      # TODO this is not ideal as it doesn't take goal diff into account
      plist = sorted(pointslist, key=itemgetter('points')) 
      plist.reverse()
      return json.dumps(plist)
      
      
class jsonGoalsSince:
  """
      Returns all goals scored since the client's maxgoalid
      jsonGoalUpdates supports OPTIONS and GET
      jsonGoalUpdates accepts optional parameter league (e.g. bl1)
      jsonGoalUpdates accepts required int parameter maxgoalid
      If the client does not provide maxgoalid the database maxgoalid is used
      meaning that nothing at all is returned to the client
  """
  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self,maxgoalid):
    web.header("Access-Control-Allow-Origin", "*")
    web.header('Content-Type','application/json')
    league = web.input(league=None).league
    if not league:
      league = getDefaultLeague()
    if not maxgoalid:
      return json.dumps({'error':'no maxgoalid provided'})
    else:
      try:
        maxgoalid = int(maxgoalid)
      except ValueError:
        return json.dumps({'error':'maxgoalid must be an integer'})
      matches = api.getMatchGoalsWithFlaggedUpdates(maxgoalid,league=league)
      matches['maxgoalid'] = api.getMaxGoalID(league=league)
      return json.dumps(matches)

class jsonMatchesUpcoming:
  """ Returns matches for current_matchday +1
  """
  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self):
    web.header("Access-Control-Allow-Origin", "*")
    web.header('Content-Type','application/json')
    season = web.input(season=None).season
    league = web.input(league=None).league
    limit = web.input(limit=None).limit
    if not limit:
      limit = 20
    else:
      try:
        limit = int(limit)
      except:
        return json.dumps({'error':'limit must be an integer'})
    if not league:
      league = getDefaultLeague()
    if not season:
      season = getCurrentSeason()
    matches = api.getMatchesUpcoming(limit=limit)
    return json.dumps(matches)

class jsonMaxGoalID:
  """ 
      Find the max (highest) goal id in the database
      jsonMaxGoalID supports OPTIONS and GET
      GET accepts optional parameter 'league' which is a string such as bl1
      GET returns a json object in form {'maxgoalid':int()}
  """

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self):
    web.header("Access-Control-Allow-Origin", "*")
    web.header('Content-Type','application/json')
    league = web.input(league=None).league
    if not league:
      league = getDefaultLeague()
    try:
      maxgoalid = api.getMaxGoalID(league)
    except Exception,e:
      print e
      return json.dumps({'error':'could not retrieve max\
             goal id for %s'%league})
    else:
      return json.dumps({'maxgoalid':maxgoalid})
      
class jsonTeams:
  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*")
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS")
    web.header("Access-Control-Allow-Headers", "Content-Type")
    web.header("Access-Control-Allow-Credentials", "false")
    web.header("Access-Control-Max-Age", "60")
    return None
    
  def GET(self):
    web.header("Access-Control-Allow-Origin", "*")
    web.header('Content-Type','application/json')
    league = web.input(league=None).league
    season = web.input(season=None).season
    if not league:
      league = getDefaultLeague()
    if not season:
      season = getCurrentSeason()
    teams = api.getTeams(league=league,season=season)
    return json.dumps(teams)

class jsonMatch:
  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None
    
  def GET(self,matchID):
    web.header("Access-Control-Allow-Origin", "*")
    web.header('Content-Type','application/json')
    try:
      mid = int(matchID)
    except ValueError:
      return json.dumps({'error':'matchID must be an integer'})
    else:
      try:
        m = api.getMatchByID(mid)
      except Exception,e:
        print e
        return json.dumps({'error':'could not return match with id %d'%mid})
      else:
        return json.dumps(m)

class jsonMatchday:
  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None
    
  def GET(self,matchday):
    web.header("Access-Control-Allow-Origin", "*")
    web.header('Content-Type','application/json')
    try:
      mid = int(matchday)
    except ValueError:
      return json.dumps({'error':'matchday must be an integer'})
    else:
      if mid == 0: # interpret this as asking for the current matchday
        m = api.getMatchesByMatchday(getCurrentMatchday())
        return json.dumps(m)
      if mid > 34:
        return json.dumps({'error':'matchday cannot be greater than 34'})
      try:
        m = api.getMatchesByMatchday(mid)
      except Exception,e:
        return json.dumps({'error':'could not return matchday with id %d'%mid})
      else:
        return json.dumps(m)

    
if __name__ == "__main__":
  application = web.application(urls, globals())#.wsgifunc()
  #print 'Serving on 8088...'
  #WSGIServer(('', 8088), application).serve_forever()
  application.run()
