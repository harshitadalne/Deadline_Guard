from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey
from backend.models.base import Base


class TimeLog(Base):
    __tablename__ = "timelogs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Float, nullable=True)
