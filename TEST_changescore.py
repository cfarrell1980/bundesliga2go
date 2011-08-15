#!/usr/bin/python
# This script starts an apscheduler which changes the scores of
# bundesliga games randomly for testing purposes. Do not use it
# on a production system as it will permanently change the scores.
# The only way to revert to the real scores is to delete the
# sqlite database and start jsonServer.py again
#
from apscheduler.scheduler import Scheduler
from random import choice
from bundesligaORM import *
from bundesligaAPI import BundesligaAPI
from bundesligaHelpers import shortcuts
from datetime import datetime
session = Session()
tick = Scheduler()
api = BundesligaAPI()

@tick.interval_schedule(seconds=20)
def changescores():
  matchtime = datetime.strptime('2011-08-06 16:00','%Y-%m-%d %H:%M')
  active = api.getActiveMatches(None,None,matchtime)
  tochange = []
  for match in active:
    while len(tochange) < 3:
      pick = choice(active)
      if pick not in tochange:
        tochange.append(pick)
  for m in tochange:
    matchobj = session.query(Match).filter(Match.id==m['matchID']).one()
    pickteam = choice([0,1])
    goalchoice = choice(range(0,10))
    if pickteam == 0:
      print "TEST: changing score of %s from %d to %d"%(shortcuts[matchobj.teams[pickteam].id],matchobj.pt1,goalchoice)
      matchobj.pt1 = goalchoice
    else:
      print "TEST: changing score of %s from %d to %d"%(shortcuts[matchobj.teams[pickteam].id],matchobj.pt2,goalchoice)
      matchobj.pt2 = goalchoice
  session.commit()
    
  

if __name__ == '__main__':
  tick.run()

