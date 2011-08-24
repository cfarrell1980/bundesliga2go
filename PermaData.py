# -*- coding: utf-8 -*-

'''
Copyright (c) 2011, Ciaran Farrell, Vladislav Lewin
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

Neither the name of the authors nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
from datetime import datetime
from OpenLigaDB import OpenLigaDB
oldb = OpenLigaDB()
current_year = datetime.now().year

DBASE = "bundesliga2.sqlite" # Name of the database file being used
DEFAULT_LEAGUES = ['bl1','bl2'] # The only leagues we are interested in
DEFAULT_LEAGUE = DEFAULT_LEAGUES[0] # Use the 1. Bundesliga as default

def getCurrentSeason():
  """The current_season depends on the time of year. For example, in May
     2011 the current_season is 2010. The current_season changes when the
     season begins in August. Thus, check if the month is greater than
     July (7th month). If so, return the current year. Otherwise return
     last year
  """
  this_year,this_month = datetime.now().year,datetime.now().month
  last_year = this_year-1
  if this_month > 7:
    return this_year
  else:
    return last_year

def getCurrentMatchDay(league=DEFAULT_LEAGUE):
  """The current matchday changes mid week when the season is underway.
     The openligadb API provides a method to get it. This function simply
     uses that APIGetCurrentGroupOrderID 
  """
  cmd = oldb.GetCurrentGroupOrderID(league)
  return cmd

def getDefaultSeasons():
  if getCurrentSeason() == current_year:
    seasons = [current_year,current_year-1]
  else:
    seasons = [getCurrentSeason(),getCurrentSeason()-1]
  return seasons

DEFAULT_SEASONS = getDefaultSeasons()  
DEFAULT_SEASON = DEFAULT_SEASONS[0]

teamShortcuts = {40: 'FCB',9:'S04',134:'BRE',6:'B04',16:'FVB',7:'BVB',
             131:'WOB',87:'BMG',76:'FCK',112:'SCF',81:'MO5',91:'FFM',
             65:'1FCK',98:'FCP',123:'HOF',79:'1FCN',55:'H96',100:'HSV',
             54:'BSC',129:'BOC',105:'KSC',83:'DSC',93:'FCE',125:'M60',
             185:'F95',23:'AAC',107:'MSV',95:'FCA',173:'RWO',80:'FCU',
             66:'AUE',36:'OSN',115:'SGF',31:'SCP',171:'FCI',172:'FSV',
             29:'OFF',69:'CZJ',127:'TUK',174:'SWW',102:'ROS'
            }

current_season = getCurrentSeason()
current_matchday = getCurrentMatchDay()

