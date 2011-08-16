"""
A scheduler that uses APScheduler (http://packages.python.org/APScheduler/) to
schedule a regular slow poll to check if there is a match in progress.  If there
is a match in progress then a faster poll is started. The faster poll updates the
local database with data from upstream. You can install the python-apscheduler
package from devel:languages:python on openSUSE or with easy_install from PyPi
"""
from apscheduler.scheduler import Scheduler
import sys,time,signal
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
matches = []

def updateMatchTimes():
  global matches
  session = Session()
  known_md = session.query(Match.startTime,Match.endTime).join(League).filter(and_(League.name==DEFAULT_LEAGUE,League.season==current_bundesliga_season())).all()
  for md in known_md:
    matches.append(md)
  matches = list(set(matches)) # reduce num. matches by half as many take place at same time
  logger.info("updateMatchTimes - wrote %d matches to global matches list"%len(matches))

@slow.interval_schedule(seconds=30) # this should be configurable through bundesliga.conf
def hiFreq():
  league=DEFAULT_LEAGUE
  season=current_bundesliga_season()
  global match_in_progress,matches
  if not len(matches):
    match_in_progress = False
  else:
    now = datetime.now()
    do_update = False
    then = now+timedelta(minutes=30)
    for m in matches:
      if (m[0] < now and m[1] > now):
        do_update = True
        break
      elif m[0] > now and m[0] <= then:
        smin = int(((then-now).seconds)/60)
      else:
        pass
    if do_update:
      match_in_progress = True
      logger.info("hiFreq - match in progress. Calling api.updateLocalCache()")
      api.updateLocalCache(league,season)
    else:
      logger.info("hiFreq - nothing to do")
      match_in_progress = False
      
 
@slow.interval_schedule(seconds=60*2)
def sync():
  '''Perform a sync every so often anyway? Is this really needed?'''
  logger.info("sync - standard sync called to sync openligadb.de data to local cache...")
  s = time.time()
  league = DEFAULT_LEAGUE
  season = current_bundesliga_season()
  api.updateLocalCache(league,season)
  e = time.time()
  took = e-s
  logger.info("sync - finished syncing. It took %f seconds"%took)

@slow.interval_schedule(seconds=90)
def fillFuture():
  logger.info("fillFuture - calling updateMatchTimes()")
  updateMatchTimes()

if __name__ == '__main__':
  ''' If the script is called directly from the cmdline then just start
      the scheduler and run forever...
  '''
  try:
    slow.start()
    signal.pause() # necessary because of http://www.velocityreviews.com/forums/t741696-apscheduler-error.htm
  except KeyboardInterrupt:
    sys.stdout.write("\r")
    sys.stdout.flush()
    sys.stdout.write("Bye bye\n")
    exit(0)
  else:
    pass
