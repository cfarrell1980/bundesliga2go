"""
A scheduler that uses APScheduler (http://packages.python.org/APScheduler/) to
schedule a regular slow poll to check if there is a match in progress.  If there
is a match in progress then a faster poll is started. The faster poll updates the
local database with data from upstream. You can install the python-apscheduler
package from devel:languages:python on openSUSE or with easy_install from PyPi
"""
from apscheduler.scheduler import Scheduler
import sys
from bundesligaORM import *
from sqlalchemy.sql import and_,or_
from datetime import datetime,timedelta
# Start the scheduler
sched = Scheduler()
session = Session()
# Schedule job_function to be called every two hours
@sched.interval_schedule(seconds=10)
def job_function():
    now = datetime.now()
    end = now+timedelta(minutes=115)
    matches =  session.query(Match).filter(and_(Match.startTime <= now,(and_(Match.endTime>=now,Match.endTime<=end)))).all()
    if len(matches):
      print "%d matches in progress"%len(matches)
      return False
    else:
      print "No matches in progress"
      return True

try:
  sched.run()
except KeyboardInterrupt:
  sys.stdout.write("\r")
  sys.stdout.flush()
  sys.stdout.write("Bye bye\n")
  exit(0)
else:
  pass
