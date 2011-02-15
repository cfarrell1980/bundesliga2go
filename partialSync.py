#!/usr/bin/env python
# -*- coding: utf-8 -*-
cron = False
import time,json,datetime,os,sys
if len(sys.argv) == 2:
 if sys.argv[1] == '--cron':
   cron = True
from bundesligaAPI import BundesligaAPI
from bundesligaORM import *
from OpenLigaDB import OpenLigaDB
from sqlalchemy.sql import and_,or_,not_
from bundesligaLogger import logger
from bundesligaHelpers import write_qa,DEFAULT_LEAGUE,current_bundesliga_matchday
from bundesligaHelpers import current_bundesliga_season
api = BundesligaAPI()
cursor = OpenLigaDB()

global qa,league,season
qa = os.path.abspath(os.path.join(os.getcwd(),'qa.json'))
league,season = DEFAULT_LEAGUE,current_bundesliga_season()
rnow = datetime.datetime.now()
if rnow.weekday() < 4: # less than Friday?
  if os.path.isfile(qa):
    mtime = os.stat(qa).st_mtime

session = Session()
logger.info("partialSync - checking if there is currently a match in progress for %s"%rnow)
matches = session.query(Match).filter(and_(Match.startTime<=rnow,Match.endTime>=rnow)).all()
if len(matches)==0:
  logger.info("partialSync - currently no matches in progress")
else:
  logger.info("partialSync - currently %d matches in progress"%len(matches))
  print "%d matches in progress. This should be handed of to a subcron job"%len(matches)

# SYNC OPENLIGADB DATA TO LOCAL CACHE IF NECESSARY
def doSync():
 logger.info("partialSync - syncing openligadb.de data to local cache...")
 s = time.time()
 api.updateLocalCache(league,season)
 e = time.time()
 took = e-s
 logger.info("partialSync - finished syncing. It took %f seconds"%took)
 return True

# GET CURRENT MATCHDAY FROM OPENLIGADB
def doCmd():
 logger.info("partialSync - now looking for the current matchday upstream")
 s1 = time.time()
 cmd = current_bundesliga_matchday(league,force_update=True)
 s2 = time.time()
 t1=s2-s1
 logger.info("partialSync - current matchday is %d according to openliga.db. \
Call took %f seconds"%(cmd,t1))
 return cmd

# GET LAST UPDATE TIME OF LEAGUE SEASON
def doLmu():
 logger.info("partialSync - now looking for last upstream mtime of DEFAULT_LEAGUE and current season")
 s1 = time.time()
 lmu = cursor.GetLastChangeDateByLeagueSaison(league,season)
 s2 = time.time()
 logger.info("partialSync - last upstream modification of DEFAULT_LEAGUE and current season \
was %s"%lmu.strftime("%Y-%m-%dT%H:%M:%S"))
 return lmu

# WRITE THE VOLATILE STUFF TO A JSON FILE
def doWrite(cmd,lmu):
 t1 = time.time()
 logger.info("partialSync - storing volatile data in a JSON file")
 write_qa(cmd,lmu=lmu)
 t2 = time.time()
 t = t2-t1
 logger.info("partialSync - dumped volatile data to JSON file. Took %f seconds"%t)

if __name__ == '__main__':
  if cron:
    logger.info("partialSync - called by cron")
  t1 = time.time()
  doSync()
  cmd = doCmd()
  lmu = doLmu()
  doWrite(cmd,lmu)
  t2 = time.time()
  total = t2-t1
  logger.info("partialSync - script completed. Took %f seconds in total"%total)



