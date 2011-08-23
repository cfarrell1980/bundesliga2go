#!/usr/bin/env python
from apscheduler.scheduler import Scheduler
from datetime import datetime
from api import localService
from sync import SyncAPI
import signal
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
