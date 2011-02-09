#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time,json
from bundesligaAPI import BundesligaAPI
from OpenLigaDB import OpenLigaDB
from bundesligaLogger import logger
from bundesligaHelpers import DEFAULT_LEAGUE,current_bundesliga_season,current_bundesliga_matchday
api = BundesligaAPI()
cursor = OpenLigaDB()

global qa,league,season
qa = 'qa.json'
league,season = DEFAULT_LEAGUE,current_bundesliga_season()

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
 cmd = current_bundesliga_matchday(league)
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
 qa = "qa.json"
 t1 = time.time()
 logger.info("partialSync - storing volatile data in a JSON file")
 qa_info = {'cmd':cmd,'lmu':lmu.strftime("%Y-%m-%dT%H:%M:%S")}
 fd = open(qa,'w')
 json.dump(qa_info,fd)
 fd.close()
 t2 = time.time()
 t = t2-t1
 logger.info("partialSync - dumped volatile data to JSON file. Took %f seconds"%t)

if __name__ == '__main__':
  t1 = time.time()
  doSync()
  cmd = doCmd()
  lmu = doLmu()
  doWrite(cmd,lmu)
  t2 = time.time()
  total = t2-t1
  logger.info("partialSync - script completed. Took %f seconds in total"%total)



