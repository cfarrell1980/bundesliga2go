#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from bundesligaAPI import BundesligaAPI
from bundesligaLogger import logger
from bundesligaHelpers import DEFAULT_LEAGUE,current_bundesliga_season
api = BundesligaAPI()
logger.info("Syncing openligadb.de data to local cache...")
s = time.time()
api.updateLocalCache(DEFAULT_LEAGUE,current_bundesliga_season())
e = time.time()
took = e-s
logger.info("Finished syncing. It took %f seconds"%took)

