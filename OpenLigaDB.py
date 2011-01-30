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

# -*- coding: utf-8 -*-
from suds.client import Client
from suds import sudsobject

class OpenLigaDB:

  def __init__(self,timeout=8):
    '''
    Initialise the suds client using the openligadb webservices url
    '''
    self.opendburl = "http://www.OpenLigaDB.de/Webservices/Sportsdata.asmx?WSDL"
    try:
      self.client = Client(self.opendburl,timeout=timeout)
    except:
      raise StandardError,"Connection to openligadb.de timed out..."

  def GetAvailGroups(self,leagueShortcut,leagueSaison):
    '''
    Gibt eine Liste der bereits eingetragenen Spiel-Einteilungen (Spieltag,
    Vorrunde, Finale, ...) der als Parameter zu übergebenden Liga + Saison zurueck.
    return self.client.service.GetAvailGroups(leagueShortcut,leagueSaison)
    '''
    return self.client.service.GetAvailGroups(leagueShortcut,leagueSaison)

  def GetAvailLeagues(self):
    '''Gibt eine Struktur aller verfügbaren Ligen zurück! Erwartet keine Parameter'''
    return self.client.service.GetAvailLeagues()

  def GetAvailLeaguesBySports(self,sportID):
    '''
    Gibt eine Struktur aller verfügbaren Ligen für die zu übergebende SportID zurück.
    Diese ist aus 'GetAvailSports()' zu entnehmen!
    '''
    return self.client.service.GetAvailLeaguesBySports(sportID)

  def GetAvailSports(self):
    '''
    Gibt eine Liste der verfügbaren Sportarten, für welche gültige Ligen bestehen, zurück.
    Erwartet keine Parameter
    '''
    return self.client.service.GetAvailSports()

  def GetCurrentGroup(self,leagueShortcut):
    '''
    Gibt die aktuelle Group (entspricht z.B. bei der Fussball-Bundesliga dem 'Spieltag')
    des als Parameter zu übergebenden leagueShortcuts (z.B. 'bl1') aus. Der aktuelle
    Spieltag wird jeweils zur Hälfte der Zeit zwischen dem letzten Spiel des letzten
    Spieltages und dem ersten Spiel des nächsten Spieltages erhöht.
    '''
    return self.client.service.GetCurrentGroup(leagueShortcut)

  def GetCurrentGroupOrderID(self,leagueShortcut):
    '''
    Gibt die aktuelle groupOrderID (entspricht z.B. bei der Fussball-Bundesliga dem
    'Spieltag') des als Parameter zu übergebenden leagueShortcuts (z.B. 'bl1') aus.
    Der aktuelle Spieltag wird jeweils zur Hälfte der Zeit zwischen dem letzten Spiel
    des letzten Spieltages und dem ersten Spiel des nächsten Spieltages erhöht.
    '''
    return self.client.service.GetCurrentGroupOrderID(leagueShortcut)

  def GetFusballdaten(self,Spieltag,Liga,Saison,Userkennung):
    '''
    Gibt eine Struktur deutscher Fussball-Spieldaten zurueck. Diese Methode steht
    nur noch aus Gründen der Kompatibilität zu älteren Applikationen zur Verfügung.
    Bitte nutzen sie vorrangig die GetMatchdata... - Methoden!
    '''
    return self.client.service.GetFusballdaten(Spieltag,Liga,Saison,Userkennung)

  def GetGoalGettersByLeagueSaison(self,leagueShortcut,leagueSaison):
    '''
    Gibt eine Liste der GoalGetter der als Parameter zu übergebenden Liga + Saison
    zurueck.
    '''
    return self.client.service.GetGoalGettersByLeagueSaison(leagueShortcut,leagueSaison)

  def GetGoalsByMatch(self,MatchID):
    '''
    Gibt eine Liste aller Goals des als Parameter zu übergebenden Match zurueck.
    '''
    return self.client.service.GetGoalsByMatch(MatchID)

  def GetLastChangeDateByGroupLeagueSaison(self,groupOrderID,leagueShortcut,leagueSaison):
    '''
    Gibt das Datum der letzten Änderung in der als Parameter zu übergebenden
    Liga + Saison zurueck. Kann verwendet werden, um clientseitig unnötige
    Abfragen zu vermeiden (Cache)
    '''
    return self.client.service.GetLastChangeDateByGroupLeagueSaison(groupOrderID,
      leagueShortcut,leagueSaison)

  def GetLastChangeDateByLeagueSaison(self,leagueShortcut,leagueSaison):
    '''
    Gibt das Datum der letzten Änderung in der als Parameter zu übergebenden
    Liga + Saison zurueck. Kann verwendet werden, um clientseitig unnötige
    Abfragen zu vermeiden (Cache)
    '''
    return self.client.service.GetLastChangeDateByLeagueSaison(leagueShortcut,leagueSaison) 

  def GetLastMatch(self,leagueShortcut):
    '''
    Gibt eine Struktur des zuletzt ausgetragenen Spieles der als Parameter zu
    übergebenden Liga zurueck.
    '''
    return self.client.service.GetLastMatch(leagueShortcut)

  def GetMatchByMatchID(self,MatchID):
    '''
    Gibt eine Struktur des Spieles der als Parameter zu übergebenden MatchID zurueck.
    '''
    return self.client.service.GetMatchByMatchID(MatchID)

  def GetMatchdataByGroupLeagueSaison(self,groupOrderID,leagueShortcut,leagueSaison):
    '''
    Gibt eine Struktur von Sport-Spieldaten zurueck. Als Parameter werden eine
    groupOrderID (zu entnehmen aus GetAvailGroups, entspricht z.B. bei der
    Fussball-Bundesliga dem Spieltag), der Liga-Shortcut (z.B. 'bl1') sowie die
    Saison (aus GetAvailLeagues, z.B. '2009') erwartet. Das Ergebnis dieser Abfrage
    unterliegt einem serverseitigen Cache von 60 Sekunden.
    '''
    return self.client.service.GetMatchdataByGroupLeagueSaison(groupOrderID,leagueShortcut,
      leagueSaison)

  def GetMatchdataByGroupLeagueSaisonJSON(self,groupOrderID,leagueShortcut,leagueSaison):
    '''
    Gibt einen serialisiertes JSON-Objekt von Sport-Spieldaten zurueck. Als Parameter werden
    eine groupOrderID (zu entnehmen aus GetAvailGroups, entspricht z.B. bei der
    Fussball-Bundesliga dem Spieltag), der Liga-Shortcut (z.B. 'bl1') sowie die Saison
    (aus GetAvailLeagues, z.B. '2009') erwartet. Das Ergebnis dieser Abfrage unterliegt
    einem serverseitigen Cache von 60 Sekunden.
    '''
    return self.client.service.GetMatchdataByGroupLeagueSaisonJSON(groupOrderID, leagueShortcut,
      leagueSaison)

  def GetMatchdataByLeagueDateTime(self,fromDateTime,toDateTime,leagueShortcut):
    '''
    Gibt eine Struktur von Sport-Spieldaten zurueck. Die Beginn-Zeit der ausgegebenen
    Spieldaten liegt zwischen den als Parameter zu übergebenen DateTime-Werten.
    (fromDateTime <= matchBeginDateTime < toDateTime)Als weiterer Parameter wird der
    Liga-Shortcut (z.B. 'bl1') erwartet.
    '''
    return self.client.service.GetMatchdataByLeagueDateTime(fromDateTime,toDateTime,leagueShortcut)

  def GetMatchdataByLeagueSaison(self,leagueShortcut,leagueSaison):
    '''
    Gibt eine Struktur von Sport-Spieldaten aller Spiele der Liga pro Saison zurueck.
    Als Parameter werden der Liga-Shortcut (z.B. 'bl1') sowie die Saison (aus
    GetAvailLeagues, z.B. '2007') erwartet.
    '''
    return self.client.service.GetMatchdataByLeagueSaison(leagueShortcut,leagueSaison)

  def GetMatchdataByTeams(self,teamID1,teamID2):
    '''
    Gibt eine Struktur von Matches zurück, bei welchen die als Parameter übergebenen
    Teams gegeneinander spielten.
    '''
    return self.client.service.GetMatchdataByTeams(teamID1,teamID2)

  def GetNextMatch(self,leagueShortcut):
    '''
    Gibt eine Struktur des nächsten anstehenden Spieles der als Parameter zu
    übergebenden Liga zurueck.
    '''
    return self.client.service.GetNextMatch(leagueShortcut)

  def GetTeamsByLeagueSaison(self,leagueShortcut,leagueSaison):
    '''
    Gibt eine Liste aller Teams der als Parameter zu übergebenden Liga + Saison
    zurueck.
    '''
    return self.client.service.GetTeamsByLeagueSaison(leagueShortcut,leagueSaison)

