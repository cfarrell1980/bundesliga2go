#!/usr/bin/env python
from apscheduler.scheduler import Scheduler
from datetime import datetime
from sync import SyncAPI
from api import localService()
import signal
slow = Scheduler()
fast = Scheduler()
sync = SyncAPI()
api = localService()

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
