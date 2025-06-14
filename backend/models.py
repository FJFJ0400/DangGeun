from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, create_engine, func
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import Boolean
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    nickname = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())

class StudyGroup(Base):
    __tablename__ = 'studygroups'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    created_at = Column(DateTime, default=func.now())

class StudyLog(Base):
    __tablename__ = 'studylogs'
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey('studygroups.id'))
    user_id = Column(String(50))
    image_url = Column(String(255))
    comment = Column(String(100))
    created_at = Column(DateTime, default=func.now())

class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    study_log_id = Column(Integer, ForeignKey('studylogs.id'))
    created_at = Column(DateTime, default=func.now())

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    study_log_id = Column(Integer, ForeignKey('studylogs.id'))
    content = Column(Text)
    created_at = Column(DateTime, default=func.now())

class StudyStat(Base):
    __tablename__ = 'studystats'
    group_id = Column(Integer, ForeignKey('studygroups.id'), primary_key=True)
    user_id = Column(String(50), primary_key=True)
    total_logs = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    last_log_date = Column(DateTime)
    badges = Column(String(255))

class TimerLog(Base):
    __tablename__ = 'timerlogs'
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey('studygroups.id'))
    user_id = Column(String(50))  # IP 주소
    set_seconds = Column(Integer)  # 설정한 타이머(초)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

engine = create_engine('sqlite:///./study.db', connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine) 