from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    id: int
    username: str
    nickname: str
    created_at: datetime
    class Config:
        orm_mode = True

class StudyLogBase(BaseModel):
    id: int
    user_id: str  # IP 주소
    image_url: Optional[str]
    comment: Optional[str]
    created_at: datetime
    class Config:
        orm_mode = True

class LikeBase(BaseModel):
    id: int
    user_id: int
    study_log_id: int
    created_at: datetime
    class Config:
        orm_mode = True

class CommentBase(BaseModel):
    id: int
    user_id: int
    study_log_id: int
    content: str
    created_at: datetime
    class Config:
        orm_mode = True

class StudyStatBase(BaseModel):
    user_id: str  # IP 주소
    total_logs: int
    total_likes: int
    streak_days: int
    last_log_date: Optional[datetime]
    class Config:
        orm_mode = True

class TimerLogBase(BaseModel):
    id: int
    user_id: str
    set_seconds: int
    start_time: datetime
    end_time: datetime | None = None
    created_at: datetime
    class Config:
        orm_mode = True 