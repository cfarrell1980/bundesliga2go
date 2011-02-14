#!/usr/bin/python
# -*- coding: utf-8 -*-

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

import web,os,json,time,sys,contextlib,subprocess
from background import background,backgrounder
if len(sys.argv) == 2:
 if sys.argv[1] == '--apache':
  abspath = os.path.dirname(__file__)
  sys.path.append(abspath)
  os.chdir(abspath)
import web
import hashlib
from datetime import datetime
from bundesligaAPI import BundesligaAPI,AlreadyUpToDate,InvocationError,StaleData
from bundesligaLogger import logger
from OpenLigaDB import OpenLigaDB
from paste.gzipper import middleware as gzm
from partialSync import doSync as init_sync
from partialSync import doCmd as init_cmd
from partialSync import doLmu as init_lmu
from partialSync import doWrite as init_write
logger.info("jsonServer - performing initial setup including syncing from upstream...")
@contextlib.contextmanager
def spin():
   # see http://is.gd/AcCZFS
   p = subprocess.Popen(['python', 'spinner.py'])
   yield
   p.terminate()

def initSync():
  with spin():
    init_sync()
print "Performing initial sync...".rstrip("\n")
initSync()
mycmd = init_cmd()
mylmu = init_lmu()
init_write(mycmd,mylmu)
print
from bundesligaHelpers import *
logger.info("jsonServer - starting WSGI JSON server")
render_in_context = web.template.render('templates/', base='layout')
render = web.template.render('templates/')
web.config.debug = False
logger.info("Server is running in debug modus? %s"%web.config.debug)

urls = (
  '/','index',
  '/test','test',
  '/getTeams', 'getTeams',
  '/matchday','matchday',
  '/md','md',
  '/checkMD5','checkMD5',
  '/cmd','getCurrentMatchday',
  '/currentMatchDayData','getCurrentMatchdayData',
  '/w','getGoals',
  '/seasondata','seasonData',
  '/goals','getGoals',
  '/getUpdatesByMatchday','getUpdatesByMatchday',
  '/getUpdates','getUpdatesByTstamp',
  '/getUpdatesByTstamp','getUpdatesByTstamp',
  '/getData','getData'
)
render = web.template.render('bundesliga/')
#app = web.application(urls,globals(),autoreload=True)
app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()

api = BundesligaAPI()

@background
def fillDB(league,season):
  logger.info("fillDB - background function called with params league=%s season=%d"%(str(league),str(season)))
  data = api.setupLocal(league,season)

def parseRequestFundamentals():
  cbk = web.input(callback=None)
  cbk = cbk.callback
  league = web.input(league=None)
  league = league.league
  if not league: league = DEFAULT_LEAGUE
  cmd = current_bundesliga_matchday(league)
  now = datetime.now().strftime("%Y-%m-%dT%H:%M%S")
  season = web.input(season=None)
  if not season:
    logger.info("getData::GET - season undefined...")
    season = current_bundesliga_season()
  else:
    logger.info("getData::GET - trying to use client defined season %s"%season.season)
    try:
      season = int(season.season)
    except TypeError:
      logger.info("getData::GET - can't convert season %s into int"%season)
      season = current_bundesliga_season()
    else: pass
  return (cbk,league,season)


def getDataFromAPI(league,season):
  '''Because we have to respond with the same data to various calls (sometimes GET sometimes POST)
     it is better to refactor the actual retrieval of data to a separate function
  '''
  try:
    data = api.getMatchdataByLeagueSeason(league,season)
  except AlreadyUpToDate,e:
    return json.dumps({'current':1,'cmd':cmd,'tstamp':now})
  else:
    matchdaycontainer = {} #hold matchdays
    container = {}#hold matches by matchid
    for x in range(1,35):#prepare the matchday arrays
      matchdaycontainer[x] = []
    for m in data: # handle all matches in a matchday
      container[m.id] = {'t1':m.teams[0].id,
               't2':m.teams[1].id,
               'st':m.startTime.isoformat(),
               'et':m.endTime.isoformat(),
               'fin':m.isFinished,
               'pt1':m.pt1,
               'pt2':m.pt2,
               'v':m.viewers,
              }
      matchdaycontainer[m.matchday].append(m.id)
  goals = api.getGoalsByLeagueSeason(league,season)
  goalobjects,goalindex = goals[0],goals[1]
  now = datetime.now().strftime("%Y-%m-%dT%H:%M%S")
  cmd = current_bundesliga_matchday(league)
  packdict = {'tstamp':now,'matches':container,'matchdays':matchdaycontainer,'goalobjects':goalobjects,'goalindex':goalindex,'cmd':cmd}
  y = json.dumps(packdict)
  return y


class index:
  def GET(self):
    return render.index()

class worker:
  def GET(self):
    env = web.ctx.env
    print env
    cbk = web.input(callback=None)
    cbk = cbk.callback
    d = {'hello':'world','env':'notimp'}
    web.header('Cache-Control','no-cache')
    web.header('Pragma','no-cache')
    web.header('Content-Type','application/xml')
    #return "%s(%s)"%(cbk,str(json.dumps(d)))

    xml = '<?xml version=\"1.0\"?>\n'
    xml += '<note>\n'
    xml += '<to>Tove</to>\n'
    xml += '<from>Jani</from>\n'
    xml += '<heading>Reminder</heading>\n'
    xml += "<body>Dont forget me this weekend</body>\n"
    xml += "</note>\n"
    return xml

class getGoals:
  def GET(self):
    logger.info('getGoals::GET - called')
    cbk = web.input(callback=None)
    cbk = cbk.callback
    matchID = web.input(matchID=None)
    matchID = matchID.matchID
    if not matchID:
      return "%s()"%cbk
    else:
      try:
        goals = getGoalsByMatchID(matchID)
      except StandardError,e:
        return"%s('invocationError':'%s')"%(cbk,str(e))
      else:
        return "%s(%s)"%(cbk,str(json.dumps(goals)))

  def POST(self):
    logger.info('getGoals::POST - called')
    cursor = OpenLigaDB()
    web.header('Content-Type','application/json')
    web.header("Access-Control-Allow-Origin", "*")
    matchday = web.input(matchday=None)
    d = web.data().split("&")
    matchday = d[0].split("=")[1]
    league = d[1].split("=")[1]
    season = d[2].split("=")[1]
    #new_matchday_data = cursor.GetMatchdataByGroupLeagueSaison(matchday,league,season)
    #x = matchdata_to_py(new_matchday_data)
    retobj = {'matchdata':'foo','matchday':'bar'}
    return json.dumps(retobj)

  def OPTIONS(self):
    logger.info('getGoals::OPTIONS - called')
    web.header('Content-Type','application/json')
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "POST,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return json.dumps({'name':'Ciaran','job':'Bundespresident'})

class getUpdatesByTstamp:
  @backgrounder
  def GET(self):
    s1 = time.time()
    cbk = web.input(callback=u'bundesliga2go')
    cbk=cbk.callback
    tstamp=web.input(tstamp=None)
    tstamp = tstamp.tstamp
    if not tstamp:
      s2 = time.time()
      t = s2-s1
      logger.info("getUpdatesByTstamp::GET - bailing out as no tstamp. Took %f seconds"%t)
      return "%s({'invocationError':'invalid_tstamp'})"%cbk
    else:
      try:
        tstamp = datetime.strptime(tstamp,"%Y-%m-%dT%H:%M:%S")
      except:
        s2 = time.time()
        t = s2-s1
        logger.info("getUpdatesByTstamp::GET - bailing out as invalid tstamp. Took %f seconds"%t)
        return "%s({'invocationError':'invalid_tstamp'})"%cbk
      else:
        pass
    new_stamp = datetime.now()
    new_stamp_s = new_stamp.strftime("%Y-%m-%dT%H:%M:%S")
    season=web.input(season=current_bundesliga_season())
    season = int(season.season)
    league = web.input(league=DEFAULT_LEAGUE)
    league = league.league
    web.header('Content-Type','application/json')
    s2 = time.time()
    t1 = s2-s1
    logger.info('getUpdatesByTstamp::GET - parsing request took %f seconds'%t1)
    s3 = time.time()
    cmd = current_bundesliga_matchday(league)
    sx1 = time.time()
    cmdt = sx1-s3
    logger.info("getUpdatesByTstamp::GET - calling cmd took %f seconds"%cmdt)
    try:
      updates = api.getUpdatesByTstamp(league,season,tstamp)
    except StaleData,e:
      fillDB(league,season)
      d = {'cmd':cmd,'error':'noLocalCache'}
      return "%s(%s)"%(cbk,json.dumps(d))
    else:
      rd = {'tstamp':new_stamp_s,'goalobjects':updates[0],'goalindex':updates[1],'cmd':cmd}
      d = json.dumps(rd)
      s4 = time.time()
      t2 = s4-s3
      t3 = s4-s1
      logger.info("getUpdatesByTstamp::GET - parsing data from API took %f seconds"%t2)
      logger.info("getUpdatesByTstamp::GET - running entire method took %f seconds"%t3)
      return "%s(%s)"%(cbk,d)

class getUpdatesByMatchday:
  @backgrounder
  def GET(self):
    b1 = time.time()
    new_stamp = datetime.now()
    new_stamp_s = new_stamp.strftime("%Y-%m-%dT%H:%M:%S")
    cbk = web.input(callback=u'bundesliga2go')
    cbk=cbk.callback
    league = web.input(league=DEFAULT_LEAGUE)
    league = league.league
    cmd = current_bundesliga_matchday(league)
    matchday = web.input(matchday=cmd)
    try:
      matchday = int(matchday.matchday)
    except:
      d = {'cmd':cmd,'error':'invalid_matchday'}
      logger.info("getUpdatesByMatchday::GET - invalid matchday %s"%matchday.matchday)
      return "%s(%s)"%(cbk,json.dumps(d))
    else:
      if matchday not in range(1,35):
        d = {'cmd':cmd,'error':'invalid_matchday'}
        logger.info("getUpdatesByMatchday::GET - invalid matchday (1-34?) %d"%matchday.matchday)
        return "%s(%s)"%(cbk,json.dumps(d))
    season = web.input(season=current_bundesliga_season())
    try:
      season = int(season.season)
    except:
      d = {'cmd':cmd,'error':'invalid_matchday'}
      logger.info("getUpdatesByMatchday::GET - invalid season %s"%season.season)
      return "%s(%s)"%(cbk,json.dumps(d))
    else:
      pass
    web.header('Content-Type','application/json')
    b2 = time.time()
    logger.info("getUpdatesByMatchday::GET - parsing request took %f seconds"%(b2-b1))
    updates = api.getUpdatesByMatchday(league,season,matchday=matchday)
    rd = {'tstamp':new_stamp_s,'goalobjects':updates[0],'goalindex':updates[1],'cmd':cmd}
    d = json.dumps(rd)
    b_end = time.time()
    tot = b_end-b1
    logger.info("getUpdatesByMatchday::GET - running function took %f seconds"%tot)
    return "%s(%s)"%(cbk,d)

class getData:
  def OPTIONS(self):
    logger.info('getData::OPTIONS - called')
    web.header('Content-Type','application/json')
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "POST,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def POST(self):
    web.header("Access-Control-Allow-Origin", "*")
    try:
      cbk,league,season = parseRequestFundamentals()
    except:
      cbk = 'bundesliga2go'
      league = DEFAULT_LEAGUE
      season = current_bundesliga_season()
    else:
      pass
    y = getDataFromAPI(league,season)
    web.header('Content-Type','application/json')
    return json.dumps(y)

  @backgrounder
  def GET(self):
    try:
      cbk,league,season = parseRequestFundamentals()
    except:
      cbk = 'bundesliga2go'
      league = DEFAULT_LEAGUE
      season = current_bundesliga_season()
    else:
      pass
    y = getDataFromAPI(league,season)
    web.header('Content-Type','application/json')
    return "%s(%s)"%(cbk,y)

class getCurrentMatchday:
  '''
  This class is responsible for returning the current season matchday for a given league. For
  example, if the client requests the current matchday for the 1. Bundesliga, then the upstream
  server will be queried. According to the upstream documentation, the current matchday changes
  from n to n+1 in the middle of the week (presumably Wednesday). This means that from Wednesday
  to Friday, there will be no results available for the current match day (i.e. goals will show
  -1 for each team).
  '''
  def GET(self):
    cbk = web.input(callback=None)
    cbk = cbk.callback
    league = web.input(league=None)
    league=league.league
    if not league: league = DEFAULT_LEAGUE
    web.header('Cache-Control','no-cache')
    web.header('Pragma','no-cache')
    web.header('Content-Type','application/json') 
    cursor = OpenLigaDB()
    currentMatchDay = cursor.GetCurrentGroup(league)
    return "%s('cmd':'%s')"%(cbk,currentMatchDay.groupOrderID)


class getTeams:
  '''This class enables the client to have speedy access to all the teams in a specified
     league. It queries the upstream server for all teams in the league and mixes the data
     returned from upstream with locally stored supplemental data (such as team shortcut)))
  '''

  def GET(self):
    '''
    Return all the teams for specified league and year. Defaults to Bundesliga 1 for 
    the current season'''
    try:
      cbk,league,season = parseRequestFundamentals()
    except:
      cbk = 'bundesliga2go'
      league = DEFAULT_LEAGUE
      season = current_bundesliga_season()
    else:
      pass
    cmd = current_bundesliga_matchday(league)
    try:
      data = api.getTeams(league,season)
    except InvocationError:
      d = json.dumps({'invocationError':'Season %d or League %s does not exist?'%(season,league),'cmd':cmd})
      return "%s(%s)"%(cbk,d)
    else:
      d = {}
      for t in data:
        if shortcuts.has_key(t.id):
          scut = shortcuts[t.id]
        else:
          scut = None
        d[t.id] = {'name':t.name,
                 'icon':t.iconURL,
                 'short':scut}
      y = json.dumps({'cmd':cmd,'teams':d})
      return "%s(%s)"%(cbk,y)

if __name__ == '__main__':
  try:
    logger.info("jsonServer - server is listening...")
    app.run(gzm)
  except KeyboardInterrupt:
    logger.info("jsonServer - caught keyboard interrupt. Server will exit...")
    sys.exit(0)
  else:
    pass

