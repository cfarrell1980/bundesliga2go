#!/usr/bin/env python
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
from apscheduler.scheduler import Scheduler
from apscheduler import scheduler
from datetime import datetime
from bundesligaSync import bundesligaSync
from bundesligaAPI import bundesligaAPI
from bundesligaGlobals import getCurrentMatchday,getAppRoot,getCurrentMatchdayLive
import signal,json,os
slow = Scheduler()
fast = Scheduler()
sync = bundesligaSync()
api = bundesligaAPI()
from logging import StreamHandler, ERROR
import zmq
context = zmq.Context()
pub = context.socket(zmq.REQ)
pub.connect("tcp://localhost:6060")
global matches
matches = []
try:
  from StringIO import StringIO
except ImportError:
  from io import StringIO
logstream = StringIO()
loghandler = StreamHandler(logstream)
loghandler.setLevel(ERROR)
scheduler.logger.addHandler(loghandler)

#@slow.cron_schedule(day_of_week='mon-sun', hour=15, minute=11)
@slow.interval_schedule(seconds=10)
def checkForUpdates():
  ''' Rather than bombarding OpenLigaDB with requests for information that
      only changes once a week anyway, just do it once a day and cache the 
      information locally. Overwrite every time.
      Also, use the opportunity to cache the table and the top scorers. This
      means we don't have to hammer mongodb with map/reduce all the time
  '''
  current_matchday = int(getCurrentMatchdayLive())
  fd = open(os.path.join('%s/cache/'%getAppRoot(),'cmd.json'),'w')
  json.dump({'cmd':current_matchday},fd)
  fd.close()
  
  table = api.getTableOnMatchday()
  tfd = open(os.path.join('%s/cache/'%getAppRoot(),'table.json'),'w')
  json.dump(table,tfd)
  tfd.close()
  
  topscorers = api.getTopScorers()
  topfd = open(os.path.join('%s/cache/'%getAppRoot(),'topscorers.json'),'w')
  json.dump({'topscorers':topscorers},topfd)
  topfd.close()
  

@fast.interval_schedule(seconds=30)
def updateMatches(seconds=30):
  ''' Simple function run locally often. It first checks if there are
      matches in progress. If there are, for each match in progress, this
      function calls the matchToMongo method from bundesligaSync to update it.
  '''

  maxgoalid=api.getMaxGoalID()
  mip = api.getMatchesInProgress()
  if len(mip):
    for match in mip:
      sync.matchToMongo(match['matchID'])
  newmaxgoalid = api.getMaxGoalID()
  if newmaxgoalid > maxgoalid:
    newgoals = api.getGoalsSinceGoalID(maxgoalid)
    newgoals['status'] = 1
    pub.send(json.dumps(newgoals))
    pub.recv()
  else:
    pub.send(json.dumps({'status':0}))
    pub.recv()
    
if __name__ == '__main__':
  fast.start()
  slow.start()
  signal.pause()
