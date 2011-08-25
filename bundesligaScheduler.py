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
from api import localService
from sync import SyncAPI
import signal,os
api = localService()
sync = SyncAPI()
slow = Scheduler()
fast = Scheduler()

@slow.cron_schedule(day_of_week='mon-sun', hour=22, minute=02)
def checkForUpdates():
  print "Checking for updates"

@fast.interval_schedule(seconds=30)
def updateMatches():
  #mip = api.getMatchesInProgressNow(ret_dict=False)
  mip = api.getMatchesInProgressAsOf(datetime.strptime("2011-08-13 16:00",
              "%Y-%m-%d %H:%M"),ret_dict=False)
  if not len(mip):
    print "No matches in progress now"
  else:
    print "%d matches in progress"%len(mip)
    for m in mip:
      try:
        sync.syncMatch(m.id) # use the id to force the update from openligadb
      except Exception,e:
        print "failed to sync match id %d: %s"%(m.id,str(e))
      else:
        print "synced match id %d"%m.id
        
if __name__ == '__main__':
  fast.start()
  slow.start()
  signal.pause()
