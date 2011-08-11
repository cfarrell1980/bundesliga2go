
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
import hashlib,os,sys,subprocess
try:
  import json
except ImportError:
  try:
    import simplejson as json
  except ImportError:
    raise ImportError, "You need to install python-json or python-simplejson"
from bundesligaLogger import logger
DEFAULT_LEAGUE = 'bl1'

if os.environ.has_key('TMPDIR'):
  LocalStorage = os.path.join(os.environ['TMPDIR'],'bundesligaMobile')
else:
  LocalStorage = "/tmp/bundesligaMobile"

# mobile screens not wide enough to display full club names
shortcuts = {40: 'FCB',9:'S04',134:'BRE',6:'B04',16:'FVB',7:'BVB',
             131:'WOB',87:'BMG',76:'FCK',112:'SCF',81:'MO5',91:'FFM',
             65:'1FCK',98:'FCP',123:'HOF',79:'1FCN',55:'H96',100:'HSV',
             54:'BSC',129:'BOC',105:'KSC',83:'DSC',93:'FCE',125:'M60',
             185:'F95',23:'AAC',107:'MSV',95:'FCA',173:'RWO',80:'FCU',
             66:'AUE',36:'OSN',115:'SGF',31:'SCP',171:'FCI',172:'FSV',
             29:'OFF',69:'CZJ',127:'TUK',174:'SWW',102:'ROS'
            }

def json_serialize(obj):
  try:
    return obj.__dict__
  except:
    #raise TypeError(repr(obj)+" is not JSON serializable")
    return str(obj)

def remote_cmd(league):
  cursor = OpenLigaDB()
  x = cursor.GetCurrentGroupOrderID(league)
  return x

def write_qa(cmd,lmu=None,league=None,season=None):
  cmd = int(cmd)
  cursor = OpenLigaDB()
  if not league: league = DEFAULT_LEAGUE
  if not season: season = current_bundesliga_season()
  if not lmu:
    lmu = cursor.GetLastChangeDateByLeagueSaison(league,season).strftime("%Y-%m-%dT%H:%M:%S")
  else:
    if isinstance(lmu,datetime):
      lmu = lmu.strftime("%Y-%m-%dT%H:%M:%S")
  try:
    fd = open("qa.json","r")
    d = json.load(fd)
    fd.close()
  except IOError:
    fd = open("qa.json","w")
    d={}
    d['cmd'] = cmd
    d['lmu'] = lmu
    json.dump(d,fd)
    fd.close()
  else:
    if d.has_key('cmd'):
      existing_cmd = int(d['cmd'])
      logger.info('write_qa - existing_cmd is %d'%d['cmd'])
    else:
      existing_cmd = 0
    logger.info("write_qa - checking if send cmd %d is greater than existing cmd %d"%(cmd,existing_cmd))
    if cmd > existing_cmd:
      logger.info("write_qa - upstream cmd %d is greater than existing cmd %d"%(existing_cmd,cmd))
      d['cmd'] = cmd
    else:
      logger.info("write_qa - upstream cmd %d is not greater than existing cmd %d. Not touching existing one..."%(cmd,existing_cmd))
    d['lmu'] = lmu
    fd = open("qa.json","w")
    json.dump(d,fd)
    fd.close()

def current_bundesliga_matchday(league,force_update=False):
  '''The client needs to know what the current matchday is. Note that in
     some circumstances upstream may set the current matchday to be less than
     the most recent matchday. For example, if a match was cancelled and the
     replay date of the match is post the the most current matchday, then for
     the day that the match is being played, upstream may revert the matchday.
  '''
  if force_update:
    cmd = remote_cmd(league)
    write_qa(cmd)
    return cmd
  else:
    try:
      fd = open("qa.json","r")
      d = json.load(fd)
      fd.close()
    except IOError:#file not there - probably on first run
      cursor = OpenLigaDB()
      x = cursor.GetCurrentGroupOrderID(league)
      write_qa(x)
      return x
    else:
      return int(d['cmd'])

def current_bundesliga_season():
  ''' openligadb declares the year for any bundesliga season to be the
      year in which the season started. Therefore, even if we currently
      have February 2011, the year/season will be defined as 2010
      because that season started in 2010. Accordingly, this function
      simply checks the current year and returns it if we are in the 
      period August to December. If we are in the period January to
      July the function returns current year - 1 '''
  now = datetime.now()
  current_year = now.year
  current_month = now.month
  if current_month < 7:
    return int(current_year-1)
  else:
    return int(current_year)

# Won't work with python 2.5 and not needed anyway
#def checksum(thefile):
#  md5 = hashlib.md5()
#  with open('%s'%thefile,'rb') as f:
#    for chunk in iter(lambda: f.read(8192), ''):
#      md5.update(chunk)
#  return str(md5.hexdigest()).encode('utf-8')

def tstamp_to_md5(tstamp):
  '''Converts the timestamp we get back from OpenLigaDB to md5.
     This md5 value is sent to the mobile client. Every request
     from the mobile client is thereafter checked for the md5.
     The client md5 can be compared with the updated OpelLigaDB
     md5 to determine if the client's data cache is up to date
  '''
  md5 = hashlib.md5()
  md5.update(tstamp.strftime("%Y%m%d%H%M%s"))
  return md5.hexdigest()

def teamIconCssExists():
  '''Check to see if static/css/teamicons.css exists. If it does
     not exist, it means that it needs to be generated.'''
  cssfile = os.path.join(os.getcwd(),'static/css/teamicons.css')
  if not os.path.isfile(os.path.abspath(cssfile)):
    return False
  else:
    return True

def createTeamIcons():
  '''Create static/img/teams.png and static/css/teamicons.css by
     downloading the individual team icons for the league and
     season, stitching them together to create teams.png and then
     creating the appropriate CSS to reference the individual
     icons by position'''
  mkteamicons = subprocess.Popen(['python', 'mkteamicons.py'], shell=False,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  return
