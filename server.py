# -*- coding: utf-8 -*-

'''
Copyright (c) 2011, Ciaran Farrell, Vladislav Lewin
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
import web,json,re,os,sys
from api import localService
from sync import SyncAPI
from PermaData import DBASE,getCurrentMatchDay,getCurrentSeason,\
    getDefaultLeague
from datetime import datetime,timedelta
from subprocess import Popen,PIPE
from operator import itemgetter
api = localService()
sync = SyncAPI()
def SYNC():
  ''' This function just calls the sync methods in the correct order. Note that
      the methods called take quite a while to run (especially syncTeams) so it
      does not make sense to call this function often. It is run when the
      server starts as it is not envisaged that this will happen very often
  '''
  print "syncing leagues..."
  sync.syncLeagues()
  last_match_change = api.getLastChangeToMatches()
  last_upstream_change = api.getLastUpstreamChange()
  if not last_match_change:
    print "matches were never synced - syncing season data..."
    sync.syncSeasonMatches()
  else:
      if last_upstream_change > last_match_change:
        print "local database older than upstream - syncing season data..."
        sync.syncSeasonMatches()
      else:
        print "local database up to date. Not syncing season data..."

# Check if the scheduler is running. If not, do not continue
procs = Popen(['ps', '-A', '-F'], stdout=PIPE).communicate()[0]
if not re.search('bundesligaScheduler.py',procs):
  raise StandardError,"bundesligaScheduler.py is not running - start it first!"
  sys.exit(1)
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
  '/api/teams/?','jsonTeams',
  '/api/goalupdates','jsonGoalUpdates',
  '/api/maxgoalid','jsonMaxGoalID',
  '/api/table','jsonLeagueTable',
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
    league = web.input(league=None)
    league = league.league
    if not league:
      league = getDefaultLeague()
    if not tstamp:
      mip = api.getMatchesInProgressNow()
      return json.dumps(mip)
    else:
      try:
        tstamp = datetime.strptime(tstamp,"%Y-%m-%d-%H-%M")
      except:
        return json.dumps({ 'error':'%s is an invalid tstamp.'%tstamp})
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
    season = web.input(season=None)
    league = web.input(league=None)
    season = season.season
    league = league.league
    try:
      teams = api.getTeams(league=league,season=season)
    except:
      return json.dumps({'error':'could not return team data'})
    else:
      return json.dumps(teams)
      
class jsonLeagueTable:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self):
    web.header('Content-Type','application/json')
    season = web.input(season=None)
    league = web.input(league=None)
    matchday = web.input(matchday=None)
    season = season.season
    league = league.league
    matchday = matchday.matchday
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
      
      
class jsonGoalUpdates:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self):
    web.header('Content-Type','application/json')
    league = web.input(league=None)
    league = league.league
    if not league:
      league = getDefaultLeague()
    clientmaxgoal = web.input(max_goal_id=None)
    clientmaxgoal = clientmaxgoal.max_goal_id
    if not clientmaxgoal:
      return json.dumps({'error':'missing parameter max_goal_id'})
    else:
      matches = api.getGoalsPerMatchWithFlags(clientmaxgoal,league=league)
      matches['max_goal_id'] = api.getMaxGoalID(league=league)
      return json.dumps(matches)


class jsonMaxGoalID:

  def OPTIONS(self):
    web.header("Access-Control-Allow-Origin", "*");
    web.header("Access-Control-Allow-Methods", "GET,OPTIONS");
    web.header("Access-Control-Allow-Headers", "Content-Type");
    web.header("Access-Control-Allow-Credentials", "false");
    web.header("Access-Control-Max-Age", "60");
    return None

  def GET(self):
    web.header('Content-Type','application/json')
    league = web.input(league=None)
    league = league.league
    if not league:
      league = getDefaultLeague()
    try:
      max_goal_id = api.getMaxGoalID(league)
    except:
      return json.dumps({'error':'could not retrieve max\
             goal id for %s'%league})
    else:
      return json.dumps({'max_goal_id':max_goal_id})
    
if __name__ == '__main__':
  app.run()
