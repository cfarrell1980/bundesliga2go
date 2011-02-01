# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy import Table,Column,Integer,String,DateTime
from sqlalchemy import Boolean,MetaData,ForeignKey
from sqlalchemy.orm import mapper,sessionmaker
from sqlalchemy.orm import relationship, backref
import datetime,os

dbfile = os.path.join(os.getcwd(),"bundesliga.sqlite")
engine = create_engine("sqlite:///%s"%dbfile,echo=False)
metadata = MetaData()
Session = sessionmaker(bind=engine)

def now():
  return datetime.datetime.now()

league_table = Table('league', metadata,
  Column('id', Integer, primary_key=True),
  Column('shortname', String),
  Column('fullname', String),
  Column('year', Integer),
  Column('mtime',DateTime,default=now(), onupdate=now())
)

class League(object):
  def __init__(self,fullname,shortname,year):
    self.fullname = fullname
    self.shortname = shortname
    self.year = year

  def __repr__(self):
    return "<League('%s','%s','%d')>"%(self.fullname,self.shortname,self.year)

matchday_table = Table('matchday', metadata,
  Column('id',Integer,primary_key=True),
  Column('matchdayNum',Integer),
  Column('description',String),
  Column('league_id',Integer, ForeignKey('league.id')),
  Column('mtime',DateTime,default=now(),onupdate=now())
)


class Matchday(object):
  def __init__(self,matchdayNum,description):
    self.matchdayNum = matchdayNum
    self.description = description

  def __repr__(self):
    return "<Matchday('%s','%s')>"%(self.matchdayNum,
      self.description)

match_table = Table('match',metadata,
  Column('id', Integer, primary_key=True),
  Column('startTime', DateTime),
  Column('endTime', DateTime),
  Column('isFinished',Boolean),
  Column('matchday_id', Integer, ForeignKey('matchday.id')),
  Column('mtime', DateTime,default=now(),onupdate=now())
)

class Match(object):
  def __init__(self,id,startTime,endTime,isFinished):
    self.id = id
    self.startTime = startTime
    self.endTime = endTime
    self.isFinished = isFinished

  def __repr__(self):
    return "<Match('%d','%s','%s','%s')>"%(self.id,self.startTime,
      self.endTime,self.isFinished)

goal_table = Table('goal',metadata,
  Column('id', Integer, primary_key=True),
  Column('scorer', String),
  Column('minute', Integer),
  Column('penalty', Boolean),
  Column('for_team_id', Integer, ForeignKey('team.id'),nullable=False),
  Column('match_id', Integer, ForeignKey('match.id'),nullable=False),
  Column('mtime',DateTime,default=now(),onupdate=now())
  )

class Goal(object):
  def __init__(self,scorer,minute,penalty=False):
    self.scorer = scorer
    self.minute = minute
    self.penalty = penalty

  def __repr__(self):
    return "<Goal('%s','%s','%s')>"%(self.scorer,self.minute,self.penalty)

team_table = Table('team',metadata,
  Column('id',Integer,primary_key=True),
  Column('name',String),
  Column('iconURL',String),
  Column('shortcut',String),
  Column('mtime',DateTime,default=now(),onupdate=now())
  )

class Team(object):
  def __init__(self,id,name,iconURL,shortcut):
    self.id = id
    self.name = u"%s"%name.decode('utf-8')
    self.iconURL = iconURL
    self.shortcut = shortcut

  def __repr__(self):
    return "<Team('%d','%s','%s','%s')>"%(self.id,
                  self.shortcut,self.iconURL,self.shortcut)

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
  'matchdays':relationship(Matchday,backref='league')
})

mapper(Match,match_table,properties={
  'teams': relationship(Team,secondary=teams_matches,backref='matches'),
  'goals':relationship(Goal,backref='matches'),
})

mapper(Matchday,matchday_table,properties={'matches':relationship(Match,backref='matchday')})

mapper(Goal,goal_table)

mapper(Team, team_table,properties={'goals':relationship(Goal,backref='team')})

metadata.create_all(engine)
