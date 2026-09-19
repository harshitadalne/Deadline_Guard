from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    deadline: datetime
    estimated_duration_minutes: int
    importance: str
    difficulty: str


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    deadline: Optional[datetime] = None
    estimated_duration_minutes: Optional[int] = None
    importance: Optional[str] = None
    difficulty: Optional[str] = None
    status: Optional[str] = None


class TaskResponse(TaskBase):
    id: int
    user_id: int
    status: str
    priority_score: float
    risk_level: str
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TaskPriorityResponse(BaseModel):
    id: int
    title: str
    priority_score: float
    risk_level: str
    deadline: datetime
    estimated_duration_minutes: int
    importance: str
    status: str
    
    class Config:
        from_attributes = True
