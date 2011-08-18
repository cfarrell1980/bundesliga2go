# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy import Table,Column,Integer,String,DateTime
from sqlalchemy import Boolean,MetaData,ForeignKey
from sqlalchemy.orm import mapper,sessionmaker
from sqlalchemy.orm import backref
try:
  from sqlalchemy.orm import relationship
except ImportError:
  try:
    from sqlalchemy.orm import relation as relationship
  except ImportError:
    raise ImportError, "Tried using sqlalchemy.orm.relationship and sqlalchemy.orm.relation"
import datetime,os

dbfile = os.path.join(os.getcwd(),"bundesliga2.sqlite")
engine = create_engine("sqlite:///%s"%dbfile,echo=False)
metadata = MetaData()
Session = sessionmaker(bind=engine)

def now():
  return datetime.datetime.now()

match_table = Table('match',metadata,
  Column('id', Integer, primary_key=True),
  Column('matchTeam1',Integer,ForeignKey('team.id')),
  Column('matchTeam2',Integer,ForeignKey('team.id')),
  Column('matchStartTime', DateTime),
  Column('matchIsFinished',Boolean),
  Column('matchMatchday', Integer),
  Column('matchViewers',Integer,default=0),
  Column('matchPointsTeam1',Integer,default=0),
  Column('matchPointsTeam2',Integer,default=0),
  Column('matchLocation',String)
)

class Match(object):
  def __init__(self,matchID,matchStartTime,
               matchIsFinished,matchMatchday,matchViewers=0,matchPointsTeam1=0,
               matchPointsTeam2=0,matchLocation=None):
    self.id = matchID
    self.matchStartTime = matchStartTime
    self.matchIsFinished = matchIsFinished
    self.matchMatchday = matchMatchday
    self.matchViewers = matchViewers
    self.matchPointsTeam1 = matchPointsTeam1
    self.matchPointsTeam2 = matchPointsTeam2
    self.matchLocation = matchLocation
  def __repr__(self):
    return "<Match('%d','%s')>"%(self.id,self.matchStartTime)

goal_table = Table('goal',metadata,
  Column('id', Integer, primary_key=True),
  Column('goalScorer', String),
  Column('goalMinute', Integer),
  Column('goalIsPenalty', Boolean,default=False),
  Column('goalIsOwnGoal', Boolean,default=False),
  Column('match_id',Integer,ForeignKey('match.id')),
  Column('team_id',Integer,ForeignKey('team.id')),
  Column('goalMatchModified',DateTime,default=now(),onupdate=now())
  )

class Goal(object):
  def __init__(self,goalID,goalScorer,goalMinute,goalIsPenalty,goalIsOwnGoal):
    self.id = goalID
    self.goalScorer = u"%s"%goalScorer.decode('utf-8')
    self.goalMinute = goalMinute
    self.goalIsPenalty = goalIsPenalty
    self.goalIsOwnGoal = goalIsOwnGoal
    self.goalMatchModified = now()

  def __repr__(self):
    return "<Goal('%d','%s','%d','Penalty?:%s','OwnGoal?:%s')>"%(self.id,self.goalScorer,self.goalMinute,
             self.goalIsPenalty,self.goalIsOwnGoal)

team_table = Table('team',metadata,
  Column('id',Integer,primary_key=True),
  Column('teamShortName',String),
  Column('teamFullName',String),
  Column('teamIconUrl',String),
  )

class Team(object):
  def __init__(self,teamID,teamFullName,teamIconUrl,teamShortName=None):
    self.id = teamID
    self.teamShortName = teamShortName
    self.teamFullName = u"%s"%teamFullName.decode('utf-8')
    self.teamIconUrl = teamIconUrl

  def __repr__(self):
    return "<Team('%d','%s','%s','%s')>"%(self.id,self.teamShortName,
                  self.teamFullName.encode('utf-8'),self.teamIconUrl)


mapper(Team, team_table,properties={
  'goals':relationship(Goal,backref='team'),
})

mapper(Match,match_table,properties={
  'team1':relationship(Team,foreign_keys=[match_table.c.matchTeam1],primaryjoin=match_table.c.matchTeam1==team_table.c.id),
  'team2':relationship(Team,foreign_keys=[match_table.c.matchTeam2],primaryjoin=match_table.c.matchTeam2==team_table.c.id),
  'goals':relationship(Goal,backref='match'),
})

mapper(Goal,goal_table)


metadata.create_all(engine)
