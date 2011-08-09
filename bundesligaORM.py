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

dbfile = os.path.join(os.getcwd(),"bundesliga.sqlite")
engine = create_engine("sqlite:///%s"%dbfile,echo=False)
metadata = MetaData()
Session = sessionmaker(bind=engine)

def now():
  return datetime.datetime.now()

league_table = Table('league', metadata,
  Column('id', Integer, primary_key=True),
  Column('name', String),
  Column('season', Integer),
  Column('mtime',DateTime,default=now(), onupdate=now())
)

class League(object):
  def __init__(self,name,season):
    self.name = name
    self.season = season

  def __repr__(self):
    return "<League('%s','%d')>"%(self.name,self.season)

match_table = Table('match',metadata,
  Column('id', Integer, primary_key=True),
  Column('startTime', DateTime),
  Column('endTime', DateTime),
  Column('isFinished',Boolean),
  Column('matchday', Integer),
  Column('viewers',Integer,default=0),
  Column('pt1',Integer,default=0),
  Column('pt2',Integer,default=0),
  Column('league_id',Integer,ForeignKey('league.id')),
  Column('mtime', DateTime,default=now(),onupdate=now())
)

class Match(object):
  def __init__(self,id,matchday,startTime,endTime,isFinished,pt1,pt2,viewers=0):
    self.id = id
    self.startTime = startTime
    self.endTime = endTime
    self.isFinished = isFinished
    self.viewers = viewers
    self.matchday = matchday
    self.pt1 = pt1
    self.pt2 = pt2

  def __repr__(self):
    return "<Match('%d','%s','%s','%s','%d','%d','%d','%d')>"%(self.id,self.startTime,
      self.endTime,self.isFinished,self.viewers,self.matchday,self.pt1,self.pt2)

goal_table = Table('goal',metadata,
  Column('id', Integer, primary_key=True),
  Column('scorer', String),
  Column('minute', Integer),
  Column('penalty', Boolean),
  Column('t1score', Integer),
  Column('t2score', Integer),
  Column('for_team_id', Integer, ForeignKey('team.id')),
  Column('match_id', Integer, ForeignKey('match.id')),
  Column('ownGoal', Boolean,default=False),
  Column('mtime',DateTime,default=now(),onupdate=now())
  )

class Goal(object):
  def __init__(self,id,scorer,minute,t1,t2,og,penalty=False):
    self.id = id
    self.scorer = u"%s"%scorer.decode('utf-8')
    self.minute = minute
    self.penalty = penalty
    self.t1score = t1
    self.t2score = t2
    self.ownGoal = og

  def __repr__(self):
    return "<Goal('%d','%s','%s','%s','%s')>"%(self.id,self.scorer,self.minute,self.penalty,self.ownGoal)

team_table = Table('team',metadata,
  Column('id',Integer,primary_key=True),
  Column('name',String),
  Column('iconURL',String),
  Column('mtime',DateTime,default=now(),onupdate=now())
  )

class Team(object):
  def __init__(self,id,name,iconURL):
    self.id = id
    self.name = u"%s"%name.decode('utf-8')
    self.iconURL = iconURL

  def __repr__(self):
    return "<Team('%d','%s','%s')>"%(self.id,
                  self.name.encode('utf-8'),self.iconURL)

teams_leagues = Table('teams_leagues', metadata,
  Column('team_id', Integer, ForeignKey('team.id')),
  Column('league_id', Integer, ForeignKey('league.id')),
  Column('mtime',DateTime,default=now(),onupdate=now())
)

teams_matches = Table('teams_matches', metadata,
  Column('team_id', Integer, ForeignKey('team.id')),
  Column('match_id', Integer, ForeignKey('match.id')),
  Column('mtime',DateTime,default=now(),onupdate=now())
)

mapper(League,league_table,properties={
  'teams': relationship(Team,secondary=teams_leagues,backref='leagues'),
  'matches':relationship(Match,backref='league')
})

mapper(Match,match_table,properties={
  'teams': relationship(Team,secondary=teams_matches,backref='matches'),
  'goals':relationship(Goal,backref='match'),
})

mapper(Goal,goal_table)

mapper(Team, team_table,properties={'goals':relationship(Goal,backref='team')})

metadata.create_all(engine)
