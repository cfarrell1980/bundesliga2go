import os
from datetime import datetime
from OpenLigaDB import OpenLigaDB
oldb = OpenLigaDB()

def getDefaultLeague():
  return 'bl1'
    
def getCurrentSeason():
  y,m = datetime.now().year,datetime.now().month
  if m <= 7:
    return y-1
  else:
    return y
    
def getCurrentMatchday(league=getDefaultLeague()):
  groupinfo = oldb.GetCurrentGroup(league)
  return int(groupinfo.groupOrderID)
  
def getTeamShortcut(teamID):
  mapping = { 65:'KOE',131:'WOB',100:'HSV',6:'B04',134:'BRE',7:'BVB',
              40:'FCB',9:'S04',87:'BMG',76:'FCK',112:'SCF',79:'FCN',
              16:'VFB',81:'M05',54:'BSC',55:'H96',123:'HOF',95:'FCA'}
  try:
    shortcut = mapping[teamID]
  except KeyError:
    return '???'
  else:
    return shortcut
    
def getAppRoot():
  return os.path.abspath(os.path.dirname(__file__))
