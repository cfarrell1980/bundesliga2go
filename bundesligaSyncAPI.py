'''
The bundesligaSyncAPI class is used only by the bundesligaSynchroniser
 which is run by bundesligaScheduler. It contains only
enough methods to determine if updates are available upstream 
and to fetch those updates. It also contains methods for storing the
data retrieved from upstream in the local database.
'''
from bundesligaORM import *
from bundesligaPermaData import teamShortcuts
from OpenLigaDB import OpenLigaDB
from datetime import datetime
oldb = OpenLigaDB()

class bundesligaSyncAPI:

  def isRemoteChange(self,league,season,matchday):
    '''Request datetime of last change for league,season,matchday
       @league: string representing shortcut of league (e.g. 'bl1')
       @season: int representing the season year (e.g. 2011)
       @matchday: int representing the matchday required (e.g. 3)
       Returns True if upstream has changed since then or False
       otherwise
    '''
    lastUpstreamChange = oldb.GetLastChangeDateByGroupLeagueSaison(matchday,league,season)
    if datetime.now() < lastUpstreamChange:
      return True
    else:
      return False

  def matchToDBase(self,matchobject):
    '''@matchobject: a Match object from openligadb.de
    Given a matchobject this method uses SQLAlchemy's merge function
    to either create a new Match object in the local database or to
    update an existing entry.
    Returns True on success or raises an exception
    '''
    mo = matchobject
    session=Session()
    matchID = int(mo.matchID)
    matchMatchday = int(mo.groupOrderID)
    matchIsFinished = mo.matchIsFinished
    matchStartTime = mo.matchDateTime
    if mo.NumberOfViewers:
      matchViewers = int(mo.NumberOfViewers)
    else:
      matchViewers = 0
    if hasattr(mo.location,'locationCity'):
      matchLocation = mo.location.locationCity.encode('utf-8')
    else:
      matchLocation = None
    try:
      print "Merging matchID %d"%matchID
      match = session.merge(Match(matchID,matchStartTime,matchIsFinished,matchMatchday,
                  matchViewers=matchViewers,matchLocation=matchLocation))
    except Exception,e:
      print str(e)
      raise
    else:
      session.commit()
    finally:
      session.close()

  def teamToDBase(self,teamobject):
    '''
    @teamobject: a Team object from openligadb.de
    Given a teamobject this method uses SQLAlchemy's merge function
    to either create a new Team object in the local database or to
    update an existing entry.
    Returns True on success or raises an exception
    '''
    to = teamobject
    session=Session()
    teamID = int(to.teamID)
    teamFullName = to.teamName.encode('utf-8')
    teamIconUrl = to.teamIconURL
    team = session.merge(Team(teamID,teamFullName,teamIconUrl))
    if not team.teamShortName:
      if shortcuts.has_key(team.id):
        team.teamShortName = teamShortcuts[team.id]
    session.commit()
    session.close()

  def goalToDBase(self,goalobject):
    '''
    @goalobject: a Goal object from openligadb.de
    Given a goalobject this method uses SQLAlchemy's merge function
    to either create a new Goal object in the local database or to
    update an existing entry.
    Returns True on success or raises an exception
    '''
    session=Session()
    session.close()
