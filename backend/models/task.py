from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from datetime import datetime
from backend.models.base import Base


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=False)
    estimated_duration_minutes = Column(Integer, nullable=False)
    importance = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    status = Column(String, default="Pending")
    priority_score = Column(Float, default=0.0)
    risk_level = Column(String, default="LOW")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
