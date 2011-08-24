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
from OpenLigaDB import OpenLigaDB
from PermaData import getCurrentSeason,DEFAULT_LEAGUE,DEFAULT_SEASON,\
    getCurrentMatchDay,teamShortcuts,DEFAULT_LEAGUES,DEFAULT_SEASONS
from orm import *
from api import localService
session = Session()
oldb = OpenLigaDB(timeout=12)
localService = localService()
class SyncAPI:

  def syncMatch(self,match):
    ''' @match: int representing openligadb.de id for the match or a
                  match object. Determine using isinstance
        @returns: None
        This method queries all data from openligadb.de for a particular
        identified match. This data is stored locally to the Match and Goal
        database objects. It relies on the syncTeams method having been run
        already. Alternatively, if this method is supplied with a match object
        from openligadb (i.e. the result of GetMatchByMatchID) the method can
        automatically recognise this and will simply sync to the loca database
        without first doing the online lookup on openligadb.de
    '''
    if isinstance(match,int):
      match = oldb.GetMatchByMatchID(match)
    matchID = int(match.matchID)
    team1 = localService.getTeamByID(int(match.idTeam1),ret_dict=False)
    team2 = localService.getTeamByID(int(match.idTeam2),ret_dict=False)
    league = localService.getLeagueByID(int(match.leagueID),ret_dict=False)
    matchDay = int(match.groupOrderID)
    isFinished = match.matchIsFinished
    startTime = match.matchDateTime
    location = None
    viewers = 0
    if hasattr(match.location,'locationCity'):
      if match.location.locationCity:
        location = match.location.locationCity.encode('utf-8')
    if match.NumberOfViewers:
      viewers = int(match.NumberOfViewers)
    m = session.merge(Match(matchID,startTime,matchDay,location=location,
        viewers=viewers,isFinished=isFinished))
    m.team1 = team1
    m.team2 = team2
    m.league = league
    team1goals,team2goals = [],[]
    m_goals = match.goals
    if hasattr(m_goals,'Goal'):
      if isinstance(m_goals.Goal,list):
        goallist = m_goals.Goal
        for goal in goallist:
          idx = goallist.index(goal)
          if idx==0:#first goal of the game 
            if goal.goalScoreTeam1==1:
              team1goals.append(goal)
            else:
              team2goals.append(goal)
          else: #not the first goal of the game
            previous_score = goallist[idx-1]
            if goal.goalScoreTeam1 > previous_score.goalScoreTeam1:
              team1goals.append(goal)
            else: 
              team2goals.append(goal)
    for goal in team1goals:
      # We don't want to store None types in the database to represent bool
      if not goal.goalPenalty:
        gp = False
      else:
        gp = True
      if not goal.goalOwnGoal:
        gog = False
      else:
        gog = True
      g = session.merge(Goal(int(goal.goalID),goal.goalGetterName.encode('utf-8'),
              int(goal.goalMatchMinute),wasPenalty=gp,wasOwnGoal=gog))
      g.match = m
      team1.goals.append(g)
    for goal in team2goals:
      g = session.merge(Goal(int(goal.goalID),goal.goalGetterName.encode('utf-8'),
              int(goal.goalMatchMinute),wasPenalty=goal.goalPenalty,
              wasOwnGoal=goal.goalOwnGoal))
      g.match = m
      team2.goals.append(g)
    session.commit()
    
  def syncSeasonMatches(self,league=DEFAULT_LEAGUE,season=getCurrentSeason()):
    '''
    '''
    matchdata = oldb.GetMatchdataByLeagueSaison(league,season)
    matches = matchdata.Matchdata
    for match in matches:
      self.syncMatch(match)

  def syncTeams(self,league=DEFAULT_LEAGUE,season=getCurrentSeason()):
    ''' @league:  string containing shortcut of league (e.g. 'bl1')
        @season:  int representing the season request (e.g. 2011)
        @returns: None
        This method is responsible for querying openligadb.de for data
        for all teams in the requested league and requested season. This
        data is the stored in the local database. This method relies on
        the syncLeagues method being run beforehand as this method is
        responsible for creating the team->league relationship
    '''
    team = oldb.GetTeamsByLeagueSaison(league,season)
    league = localService.getLeagueByShortcutSeason(league,
              season,ret_dict=False)
    teams = team.Team
    for team in teams:
      if teamShortcuts.has_key(int(team.teamID)):
        shortName = teamShortcuts[int(team.teamID)]
      else:
        # mail admin - should add the shortcut to teamShortcuts
        shortName = None
      t = session.merge(Team(int(team.teamID),team.teamName.encode('utf-8'),
                        shortName=shortName,iconURL=team.teamIconURL))
    session.commit()
    
  def syncLeagues(self,leagues=DEFAULT_LEAGUES,seasons=DEFAULT_SEASONS):
    league_s = oldb.GetAvailLeagues()
    leagues = league_s.League
    for league in leagues:
      if league.leagueShortcut.lower() in DEFAULT_LEAGUES:
        if int(league.leagueSaison) in DEFAULT_SEASONS:
          lleague = session.merge(League(int(league.leagueID),
            league.leagueName.encode('utf-8'),league.leagueShortcut,
            int(league.leagueSaison)))
    session.commit()


