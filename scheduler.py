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
from datetime import datetime
from sync import SyncAPI
from api import localService()
import signal
slow = Scheduler()
fast = Scheduler()
sync = SyncAPI()
api = localService()

global matches = []

@slow.cron_schedule(day_of_week='mon-sun', hour=22, minute=02)
def checkForUpdates():
  # If there is an update, sync everything
  print "Checking for updates"

@fast.interval_schedule(seconds=60)
def updateMatches():
  ''' Simple function run locally often. It first checks if there are
      matches in progress. If there are, for each match in progress, this
      function calls the syncMatch method from sync.SyncAPI to update it.
  '''
  mip = api.getMatchesInProgressNow()
  for m in mip:
    matches.append(m)
  for om in matches:
    if om not in mip:
      # Match that was in progress isFinished. Check and save result
  if len(mip):
    print "%d matches in progress..."%len(mip)
    for match in mip:
      print "updating match with id %d"%match.id
      api.syncMatch(match.id)
  else:
    print "no matches in progress"

if __name__ == '__main__':
  fast.start()
  slow.start()
  signal.pause()
