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

class StudyLog(Base):
    __tablename__ = 'studylogs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    image_url = Column(String(255))
    comment = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    user = relationship('User')

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
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    total_logs = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    last_log_date = Column(DateTime)
    badges = Column(String(255))
    user = relationship('User')

engine = create_engine('sqlite:///./study.db', connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine) 