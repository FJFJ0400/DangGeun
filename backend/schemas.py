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
    user_id: int
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
    user_id: int
    total_logs: int
    total_likes: int
    streak_days: int
    last_log_date: Optional[datetime]
    class Config:
        orm_mode = True 