from datetime import datetime
from OpenLigaDB import OpenLigaDB
oldb = OpenLigaDB()

DEFAULT_LEAGUE = 'bl1' # Use the 1. Bundesliga as default

teamShortcuts = {40: 'FCB',9:'S04',134:'BRE',6:'B04',16:'FVB',7:'BVB',
             131:'WOB',87:'BMG',76:'FCK',112:'SCF',81:'MO5',91:'FFM',
             65:'1FCK',98:'FCP',123:'HOF',79:'1FCN',55:'H96',100:'HSV',
             54:'BSC',129:'BOC',105:'KSC',83:'DSC',93:'FCE',125:'M60',
             185:'F95',23:'AAC',107:'MSV',95:'FCA',173:'RWO',80:'FCU',
             66:'AUE',36:'OSN',115:'SGF',31:'SCP',171:'FCI',172:'FSV',
             29:'OFF',69:'CZJ',127:'TUK',174:'SWW',102:'ROS'
            }

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
    return last_year
  else:
    return this_year

def getCurrentMatchDay(league=DEFAULT_LEAGUE):
  """The current matchday changes mid week when the season is underway.
     The openligadb API provides a method to get it. This function simply
     uses that APIGetCurrentGroupOrderID 
  """
  cmd = oldb.GetCurrentGroupOrderID(league)
  return cmd

current_season = getCurrentSeason()
current_matchday = getCurrentMatchDay()
current_league = DEFAULT_LEAGUE
