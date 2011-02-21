"""
A scheduler that uses APScheduler (http://packages.python.org/APScheduler/) to
schedule a regular slow poll to check if there is a match in progress.  If there
is a match in progress then a faster poll is started. The faster poll updates the
local database with data from upstream. You can install the python-apscheduler
package from devel:languages:python on openSUSE or with easy_install from PyPi
"""
from apscheduler.scheduler import Scheduler
import sys,time
from bundesligaORM import *
from bundesligaAPI import BundesligaAPI
from bundesligaLogger import logger
from bundesligaHelpers import DEFAULT_LEAGUE
from bundesligaHelpers import current_bundesliga_season
from sqlalchemy.sql import and_,or_
from datetime import datetime,timedelta
api = BundesligaAPI()
slow = Scheduler()
match_in_progress = False
slow_sync_called_once = False
future_matches = []

"""
@slow.interval_schedule(seconds=10)
def hiFreq():
  '''High frequency syncing which should ensure that we update goals quickly
     if a match is in progress. If no match is in progress then we simply
     return (after writing a log entry)
  '''
  global match_in_progress
  logger.info("hiFreq - checking if anything needs to be done...")
  if match_in_progress:
    logger.info("  -> hiFreq - match is in progress - performing update...")
    league = DEFAULT_LEAGUE
    season = current_bundesliga_season()
    logger.info("  -> hiFreq - actual update is commented out!")
    #api.updateLocalCache(league,season)
    logger.info("  -> hiFreq - finished syncing.")
    return
  else:
    logger.info("  -> hiFreq - nothing to do as no match in progress")
    return
"""

@slow.interval_schedule(seconds=10)
def hiFreq():
  league=DEFAULT_LEAGUE
  season=current_bundesliga_season()
  global future_matches,slow_sync_called_once
  if not len(future_matches):
    print "No matches in progress in the next hour..."
    return
  else:
    now = datetime.now()
    do_update = False
    then = now+timedelta(minutes=30)
    for m in future_matches:
      if (m[0] < now and m[1] > now):
        print "Found a running match!"
        do_update = True
        break
      elif m[0] > now and m[0] <= then:
        smin = int(((then-now).seconds)/60)
        print "Match will start in %d minutes..."%smin
      else:
        print m[0],now,m[1]
        print "Checked all future matches and there is no match in progress. Nor will a match start in the next 30 minutes"
    if do_update:
      print "There is a match in progress. Updating from openligadb!"
      api.updateLocalCache(league,season)
      
 
@slow.interval_schedule(seconds=60*5)
def sync():
  '''Perform a sync every so often anyway? Is this really needed?'''
  logger.info("sync - sync called to sync openligadb.de data to local cache...")
  s = time.time()
  league = DEFAULT_LEAGUE
  season = current_bundesliga_season()
  api.updateLocalCache(league,season)
  e = time.time()
  took = e-s
  logger.info("sync - finished syncing. It took %f seconds"%took)

@slow.interval_schedule(seconds=30)
def fillfuture():
  global future_matches,slow_sync_called_once
  future_matches = []
  now = datetime.now()
  later = now+timedelta(hours=24) # matches in progress in the next day 
  session=Session()
  future = session.query(Match).filter(or_(and_(Match.startTime >= now,Match.startTime <= later),and_(Match.startTime < now,Match.endTime>now,Match.endTime <=later))).all()  
  for match in future:
    future_matches.append((match.startTime,match.endTime))
  slow_sync_called_once=True
  return

"""
@slow.interval_schedule(seconds=30)
def lowFreq():
    '''Query the local database to see if any matches are currently in progress. If
       there are matches in progress, switch to a higher frequency polling job. If
       there are no matches in progress, pull any updates from upstream and exit
    '''
    logger.info('lowFreq - checking if any matches are in progress...')
    global match_in_progress
    session=Session()
    now = datetime.now()
    end = now+timedelta(minutes=115)
    matches =  session.query(Match).filter(and_(Match.isFinished==False,and_(Match.startTime <= now,(and_(Match.endTime>=now,Match.endTime<=end))))).all()
    session.close()
    if len(matches):
      match_in_progress = True
      logger.info("  -> lowFreq - %d matches in progress"%len(matches))
      return False
    else:
      match_in_progress = False
      logger.info("  -> lowFreq - no matches in progress")
      return True
"""

if __name__ == '__main__':
  ''' If the script is called directly from the cmdline then just start
      the scheduler and run forever...
  '''
  try:
    slow.run()
  except KeyboardInterrupt:
    sys.stdout.write("\r")
    sys.stdout.flush()
    sys.stdout.write("Bye bye\n")
    exit(0)
  else:
    pass
