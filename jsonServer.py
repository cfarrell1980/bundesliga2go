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

import web,os,json,time
import hashlib
from datetime import datetime
from bundesligaHelpers import *
from bundesligaAPI import BundesligaAPI,AlreadyUpToDate
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
  '/getUpdates','getUpdates',
  '/getData','getData'
)

DEFAULT_LEAGUE = 'bl1'

app = web.application(urls,globals(),autoreload=True)

api = BundesligaAPI()

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


class checkMD5:
  '''This class is responsible for accepting an MD5 checksum from the mobile client
     (or none, if the client doesn't send one) and checking it against an MD5 checksum
     generated from the timestamp of the most recent change for the dataset for the
     Bundesliga/Season on the upstream server. If the GET parameters season and league
     are missing from the client's request, the current season and the default league
     are used. The GET method will return a padded json response to the client. If the
     client sends a still valid MD5 checksum (i.e. the upstream dataset has not changed)
     then the padded json dataset to be returned to the client will be empty. If the
     upstream dataset has been changed then the server will return the new dataset plus
     the updated MD5 checksum generated from the upstream timestamp.
  '''

  def GET(self):
    update_required = False
    cbk = web.input(callback=None)
    cbk = cbk.callback
    league=web.input(league=None)
    league=league.league
    if not league:
      league = DEFAULT_LEAGUE
    season = web.input(season=None)
    season=season.season
    if not season:
      season = current_bundesliga_season()
    cursor = OpenLigaDB()
    matchday = web.input(matchday=None)
    matchday = matchday.matchday
    if not matchday:
      matchday = cursor.GetCurrentGroup(league)
      matchday = matchday.groupOrderID
    upstream_tstamp = cursor.GetLastChangeDateByGroupLeagueSaison(matchday,league,season)
    upstream_md5 = tstamp_to_md5(upstream_tstamp)
    incoming_md5 = web.input(md5=None)
    incoming_md5 = incoming_md5.md5
    web.header('Cache-Control','no-cache')
    web.header('Pragma','no-cache')
    web.header('Content-Type','application/json')

    print "md5 checksum from client: %s"%incoming_md5
    if incoming_md5:
      if incoming_md5 == upstream_md5:
        return "%s()"%cbk
      else:
        update_required = True
    else: update_required = True
    if update_required:
      new_matchday_data = cursor.GetMatchdataByGroupLeagueSaison(matchday,league,season)
      x = matchdata_to_py(new_matchday_data)
      retobj = {'md5':upstream_md5,'matchdata':x,'matchday':matchday,'env':x}
      y = str(json.dumps(retobj))
      return "%s(%s)"%(cbk,y)

class getData:
  def GET(self):
    cbk = web.input(callback=None)
    cbk = cbk.callback
    league = web.input(league=None)
    league = league.league
    if not league: league = DEFAULT_LEAGUE
    season = web.input(season=None)
    season = season.season
    if not season: season = current_bundesliga_season()
    tstamp = web.input(tstamp=None)
    #web.header('Cache-Control','no-cache')
    #web.header('Pragma','no-cache')
    web.header('Content-Type','application/json')
    if tstamp.tstamp:
      try:
        tstamp = datetime.strptime(tstamp.tstamp,"%Y-%m-%dT%H:%M:%S.%f")
      except (TypeError,ValueError):
        print "Could not format string %s as datetime. Using NoneType instead"%tstamp
      else:
        pass
    try:
      data = api.getMatchdataByLeagueSeason(league,season,tstamp)
    except AlreadyUpToDate,e:
      return "%s(%s)"%(cbk,json.dumps({'current':1}))
    else:
      container = {}
      for md in data.matchdays:
        container[md.matchdayNum] = {}
        matches = md.matches
        for m in matches: # handle all matches in a matchday
          gc = {}
          for g in m.goals:
            gc[g.id] = {'scorer':g.scorer,
                        'minute':g.minute}
          container[md.matchdayNum][m.id] = {'t1':m.teams[0].id,
                     't2':m.teams[1].id,
                     'st':m.startTime.isoformat(),
                     'et':m.endTime.isoformat(),
                     'fin':m.isFinished,
                     'v':m.viewers,
                     'g':gc,
                     'p1':m.pointsTeam1,
                     'p2':m.pointsTeam2
                    }
      y = json.dumps(container)
      return "%s(%s)"%(cbk,y)
    return "foobar"

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

class getCurrentMatchdayData:
  def GET(self):
    start = time.time()
    cbk = web.input(callback=None)
    cbk = cbk.callback
    league = web.input(league=None)
    league=league.league
    if not league: league = DEFAULT_LEAGUE
    matchday = web.input(matchday=None)
    matchday = matchday.matchday
    season = web.input(season=None)
    season = season.season
    if not season:
      season = current_bundesliga_season()
    cursor = OpenLigaDB()
    if not matchday:
      getMatchDay = cursor.GetCurrentGroup(league)
      matchday = getMatchDay.groupOrderID
    matchdayData = cursor.GetMatchdataByGroupLeagueSaison(matchday,league,season)
    print matchdayData
    end = time.time()
    print "Execution of getCurrentMatchdayData took %.2f"%(end-start)
    return "%s(%s)"%(cbk,matchdayData.decode('utf-8'))

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
    season = season.season
    if not league:
      league = DEFAULT_LEAGUE
    if not season:
      season = current_bundesliga_season()
    data = api.getTeams(league,season)
    d = {}
    for t in data:
      print dir(t)
      d[t.id] = {'name':t.name,
                 'icon':t.iconURL,
                 'short':t.shortcut}
    y = json.dumps(d)
    web.header('Cache-Control','no-cache')
    web.header('Pragma','no-cache')
    web.header('Content-Type', 'application/json')
    return "%s(%s)"%(cbk,y)

if __name__ == '__main__':
  app.run(gzm)

