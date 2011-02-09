
'''
Copyright (c) 2011, Ciaran Farrell, Vladislav Gorobets
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
import hashlib,json,os,sys

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

def current_bundesliga_matchday(league):
  '''The client needs to know what the current matchday is'''
  fd = open("qa.json","r")
  d = json.load(fd)
  fd.close()
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
  if current_month < 8:
    return int(current_year-1)
  else:
    return int(current_year)

def checksum(thefile):
  md5 = hashlib.md5()
  with open('%s'%thefile,'rb') as f:
    for chunk in iter(lambda: f.read(8192), ''):
      md5.update(chunk)
  return str(md5.hexdigest()).encode('utf-8')

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

