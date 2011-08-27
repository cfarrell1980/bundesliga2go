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
from sqlalchemy import create_engine
from sqlalchemy import Table,Column,Integer,String,DateTime
from sqlalchemy import Boolean,MetaData,ForeignKey
from sqlalchemy.orm import mapper,sessionmaker
from sqlalchemy.orm import backref
from sqlalchemy.orm import object_session
from sqlalchemy import select, func
from sqlalchemy.sql import and_
from datetime import datetime
from PermaData import DBASE
import os
try:
  from sqlalchemy.orm import relationship
except ImportError:
  try:
    from sqlalchemy.orm import relation as relationship
  except ImportError:
    raise ImportError, "Tried using sqlalchemy.orm.relationship\
    and sqlalchemy.orm.relation"


dbfile = os.path.join(os.getcwd(),DBASE)
engine = create_engine("sqlite:///%s"%dbfile,echo=False)
metadata = MetaData()
Session = sessionmaker(bind=engine)

league_table = Table('league',metadata,
  Column('id',Integer,primary_key=True),
  Column('name',String),
  Column('shortcut',String),
  Column('season',Integer)
)

class League(object):
  def __init__(self,id,name,shortcut,season):
    self.id = id
    self.name = u"%s"%name.decode('utf-8')
    self.shortcut = shortcut
    self.season = int(season)

match_table = Table('match',metadata,
  Column('id', Integer, primary_key=True),
  Column('matchTeam1',Integer,ForeignKey('team.id')),
  Column('matchTeam2',Integer,ForeignKey('team.id')),
  Column('league_id',Integer,ForeignKey('league.id')),
  Column('matchDay',Integer),
  Column('location',String),
  Column('startTime',DateTime),
  Column('viewers',Integer),
  Column('isFinished',Boolean,default=False),
  Column('modified',DateTime,default=datetime.now(),onupdate=datetime.now())
)

class Match(object):
  def __init__(self,matchID,startTime,matchDay,isFinished=False,
              location=None,viewers=0):
    self.id = matchID
    self.startTime = startTime
    self.matchDay = matchDay
    if location:
      self.location = u"%s"%location.decode('utf-8')
    self.viewers = viewers
    self.isFinished = isFinished
    self.modified = datetime.now()

  @property
  def team1goals(self):
    return object_session(self).query(Goal).filter(and_(goal_table.c.match_id==self.id,
            goal_table.c.team_id==self.team1.id)).all()

  @property
  def team2goals(self):
    return object_session(self).query(Goal).filter(and_(goal_table.c.match_id==self.id,
            goal_table.c.team_id==self.team2.id)).all()

goal_table = Table('goal',metadata,
  Column('id', Integer, primary_key=True),
  Column('scorer', String),
  Column('minute', Integer),
  Column('estTstamp',DateTime),
  Column('half',Integer,default=0),
  Column('match_id',Integer,ForeignKey('match.id')),
  Column('team_id',Integer,ForeignKey('team.id')),
  Column('wasPenalty',Boolean,default=False),
  Column('wasOwnGoal',Boolean,default=False),
  Column('modified',DateTime,default=datetime.now(),onupdate=datetime.now())
  )

class Goal(object):
  def __init__(self,goalID,goalScorer,goalMinute,
              wasPenalty=False,wasOwnGoal=False):
    self.id = goalID
    self.scorer = u"%s"%goalScorer.decode('utf-8')
    self.minute = goalMinute
    self.estTstamp = None
    self.half = 1
    self.wasPenalty = wasPenalty
    self.wasOwnGoal = wasOwnGoal
    self.modified = datetime.now()


team_table = Table('team',metadata,
  Column('id',Integer,primary_key=True),
  Column('shortName',String),
  Column('fullName',String),
  Column('iconURL',String)
  )

class Team(object):
  def __init__(self,teamID,fullName,shortName=None,iconURL=None):
    self.id = teamID
    self.shortName = shortName
    self.iconURL = iconURL
    self.fullName = u"%s"%fullName.decode('utf-8')


teams_leagues = Table('teams_leagues', metadata,
  Column('team_id', Integer, ForeignKey('team.id')),
  Column('league_id', Integer, ForeignKey('league.id')),
)

mapper(Team, team_table,properties={
  'goals':relationship(Goal,backref='team'),
})

mapper(Match,match_table,properties={
  'team1':relationship(Team,foreign_keys=[match_table.c.matchTeam1],
            primaryjoin=match_table.c.matchTeam1==team_table.c.id),
  'team2':relationship(Team,foreign_keys=[match_table.c.matchTeam2],
            primaryjoin=match_table.c.matchTeam2==team_table.c.id),
  'goals':relationship(Goal,backref='match'),
})

mapper(Goal,goal_table)

mapper(League,league_table,properties={
  'teams': relationship(Team,secondary=teams_leagues,backref='leagues'),
  'matches':relationship(Match,backref='league')
})

metadata.create_all(engine)
