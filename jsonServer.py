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

import web,os,json,time,sys
from background import background,backgrounder
if len(sys.argv) == 2:
 if sys.argv[1] == '--apache':
  abspath = os.path.dirname(__file__)
  sys.path.append(abspath)
  os.chdir(abspath)
import web
import hashlib
from datetime import datetime
from bundesligaHelpers import *
from bundesligaAPI import BundesligaAPI,AlreadyUpToDate,InvocationError,StaleData
from OpenLigaDB import OpenLigaDB
from paste.gzipper import middleware as gzm

render_in_context = web.template.render('templates/', base='layout')
render = web.template.render('templates/')
web.config.debug = False

urls = (
  '/test','test',
  '/getTeams', 'getTeams',
  '/matchday','matchday',
  '/md','md',
  '/checkMD5','checkMD5',
  '/cmd','getCurrentMatchday',
  '/currentMatchDayData','getCurrentMatchdayData',
  '/w','worker',
  '/seasondata','seasonData',
  '/goals','getGoals',
  '/getUpdatesByMatchday','getUpdatesByMatchday',
  '/getUpdates','getUpdatesByTstamp',
  '/getUpdatesByTstamp','getUpdatesByTstamp',
  '/getData','getData'
)

DEFAULT_LEAGUE = 'bl1'

#app = web.application(urls,globals(),autoreload=True)
app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()

api = BundesligaAPI()

@background
def fillDB(league,season):
  data = api.setupLocal(league,season)

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
    for x in web.ctx.env.keys():
      print "%s %s"%(x,web.ctx.env[x])
    cursor = OpenLigaDB()
    web.header('Content-Type','application/json')
    web.header("Access-Control-Allow-Origin", "*")
    matchday = web.input(matchday=None)
    d = web.data().split("&")
    matchday = d[0].split("=")[1]
    league = d[1].split("=")[1]
    season = d[2].split("=")[1]
    new_matchday_data = cursor.GetMatchdataByGroupLeagueSaison(matchday,league,season)
    x = matchdata_to_py(new_matchday_data)
    retobj = {'matchdata':x,'matchday':matchday}
    y = str(json.dumps(retobj))
    print "%s %s %s"%(matchday,league,season)
    return y

  def OPTIONS(self):
    web.header('Content-Type','application/json')
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "POST,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    print web.ctx.headers
    return json.dumps({'name':'Ciaran','job':'Bundespresident'})

class getUpdatesByTstamp:
  @backgrounder
  def GET(self):
    cbk = web.input(callback=None)
    cbk = cbk.callback
    tstamp = web.input(tstamp=None)
    tstamp = tstamp.tstamp
    league = web.input(league=None)
    league = league.league
    if not league: league = DEFAULT_LEAGUE
    cmd = current_bundesliga_matchday(league)
    season = web.input(season=None)
    season = season.season
    web.header('Content-Type','application/json')
    new_stamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    if not season:
      season = current_bundesliga_season()
    else:
      try:
        season = int(season)
      except:
        print "Could not convert season %s into int"%season
      else:
       print "Converted season into int(%d)"%season
    try:
      tstamp = datetime.strptime(tstamp,"%Y-%m-%dT%H:%M:%S")
    except:
      print "Could not parse tstamp %s into 'Y-m-dTH:M:S'"%tstamp
      return "%s({'invocationError':'invalid_tstamp'})"%cbk
    else:
      try:
        updates = api.getUpdatesByTstamp(league,season,tstamp)
      except StaleData,e:
        fillDB(league,season)
        d = {'cmd':cmd,'error':'noLocalCache'}
        return "%s(%s)"%(cbk,json.dumps(d))
      else:
        rd = {'tstamp':new_stamp,'goalobjects':updates[0],'goalindex':updates[1],'cmd':cmd}
        d = json.dumps(rd)
        return "%s(%s)"%(cbk,d)

class getUpdatesByMatchday:
  @backgrounder
  def GET(self):
    cbk = web.input(callback=None)
    cbk = cbk.callback
    matchday = web.input(matchday=None)
    matchday = matchday.matchday
    if matchday:
      try:
        matchday = int(matchday)
      except:
        print "Could not convert matchday to int...ignoring it"
        matchday = None
      else:
        print "matchday converted to int %d"%matchday
    league = web.input(league=None)
    league = league.league
    if not league: league = DEFAULT_LEAGUE
    cmd = current_bundesliga_matchday(league)
    season = web.input(season=None)
    season = season.season
    if not season:
      season = current_bundesliga_season()
    else:
      try:
        season = int(season)
      except (TypeError,AttributeError):
        print "Can't convert season %s into int"%season
        season = current_bundesliga_season()
      else: pass
    web.header('Content-Type','application/json')
    new_stamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    if not api.localLeagueSeason(league,season):
      # do this in background thread
      print "Starting background task to fill database"
      fillDB(league,season)
      d = {'cmd':cmd,'error':'noLocalCache'}
      return "%s(%s)"%(cbk,json.dumps(d))
    updates = api.getUpdatesByMatchday(league,season,matchday=matchday)
    rd = {'tstamp':new_stamp,'goalobjects':updates[0],'goalindex':updates[1],'cmd':cmd}
    d = json.dumps(rd)
    return "%s(%s)"%(cbk,d)

class getData:
  @backgrounder
  def GET(self):
    cbk = web.input(callback=None)
    cbk = cbk.callback
    league = web.input(league=None)
    league = league.league
    if not league: league = DEFAULT_LEAGUE
    cmd = current_bundesliga_matchday(league)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M%S")
    season = web.input(season=None)
    if not season:
      print "season undefined..."
      season = current_bundesliga_season()
    else:
      print "trying to use client defined season %s"%season.season
      try:
        season = int(season.season)
      except TypeError:
        print "Can't convert season %s into int"%season
        season = current_bundesliga_season()
      else: pass
    web.header('Content-Type','application/json')
    if api.localCacheValid(league,season):
      print "Local cache valid for %s %d"%(league,season)
      try:
        sq = time.time()
        data = api.getMatchdataByLeagueSeason(league,season)
        eq = time.time()
      except AlreadyUpToDate,e:
        return "%s(%s)"%(cbk,json.dumps({'current':1,'cmd':cmd,'tstamp':now}))
      else:
        matchdaycontainer = {} #hold matchdays
        container = {}#hold matches by matchid
        goalcontainer = {}
        goalindex = {}
        unfinished = 0
        for x in range(1,35):#prepare the matchday arrays
          matchdaycontainer[x] = []
        for m in data: # handle all matches in a matchday
          goalindex[m.id] = []
          if m.isFinished:
            if len(m.goals):
              for g in m.goals:
                if g.for_team_id:
                  teamID = g.for_team_id
                else:
                  teamID = None
                goalcontainer[g.id] = {'scorer':g.scorer,'pen':g.penalty,
                      'minute':g.minute,'teamID':teamID,'og':g.ownGoal}
                goalindex[m.id].append(g.id)
              goalindex[m.id].append(True) # match is finished
            else: # no goals, match is finished
              goalindex[m.id] = [None,True]
          else: # match is not finished
            unfinished += 1
            if len(m.goals):
              for g in m.goals:
                if g.for_team_id:
                  teamID = g.for_team_id
                else:
                  teamID = None
                goalcontainer[g.id] = {'scorer':g.scorer,'pen':g.penalty,
                      'minute':g.minute,'teamID':teamID,'og':g.ownGoal}
                goalindex[m.id].append(g.id)
              goalindex[m.id].append(False) # match is finished
            else: # no goals, match is not finished
              goalindex[m.id] = [False]
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
        packdict = {'tstamp':now,'matches':container,'matchdays':matchdaycontainer,'goalobjects':goalcontainer,'goalindex':goalindex,'cmd':cmd}
        y = json.dumps(packdict)
        print "%d matches not yet played"%unfinished
        return "%s(%s)"%(cbk,y)
    else:
      print "Starting background task..."
      fillDB(league,season)
      d = {'cmd':cmd,'invocationError':'noLocalCache'}
      return "%s(%s)"%(cbk,json.dumps(d))

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
    cbk = web.input(callback=None)
    league = web.input(league=None)
    season = web.input(season=None)
    cbk = cbk.callback
    league = league.league
    #web.header('Cache-Control','no-cache')
    #web.header('Pragma','no-cache')
    web.header('Content-Type', 'application/json')
    season = season.season
    if not league:
      league = DEFAULT_LEAGUE
    cmd = current_bundesliga_matchday(league)
    if not season:
      season = current_bundesliga_season()
    else:
      try:
        season = int(season)
      except (AttributeError,TypeError):
        print "Could not convert season %s to int"%season
        season = current_bundesliga_season()
      else:
        pass
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
      y = json.dumps(d)
      return "%s(%s)"%(cbk,y)

if __name__ == '__main__':
  app.run(gzm)

