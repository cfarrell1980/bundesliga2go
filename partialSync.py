#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bundesligaAPI import BundesligaAPI
from bundesligaHelpers import DEFAULT_LEAGUE,current_bundesliga_season
api = BundesligaAPI()
print "Syncing openligadb.de data to local cache..."
api.updateLocalCache(DEFAULT_LEAGUE,current_bundesliga_season())
print "Done!"

