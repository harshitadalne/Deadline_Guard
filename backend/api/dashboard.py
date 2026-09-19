import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
from backend.database.database import get_db
from backend.models.task import Task
from backend.models.user import User
from backend.api.auth import get_current_user
from backend.services.scheduler import TaskScheduler
from backend.services.workload_engine import WorkloadEngine

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get dashboard summary statistics."""
    # Get all user's tasks
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    
    # Calculate statistics
    total_tasks = len(tasks)
    pending_tasks = len([t for t in tasks if t.status == "Pending"])
    in_progress_tasks = len([t for t in tasks if t.status == "In Progress"])
    completed_tasks = len([t for t in tasks if t.status == "Completed"])
    
    # Calculate overdue tasks
    now = datetime.utcnow()
    overdue_tasks = len([
        t for t in tasks 
        if t.deadline < now and t.status not in ["Completed"]
    ])
    
    # Calculate critical and high risk tasks
    critical_tasks = len([t for t in tasks if t.risk_level == "CRITICAL" and t.status not in ["Completed"]])
    high_risk_tasks = len([t for t in tasks if t.risk_level == "HIGH" and t.status not in ["Completed"]])
    
    return {
        "total_tasks": total_tasks,
        "pending": pending_tasks,
        "in_progress": in_progress_tasks,
        "completed": completed_tasks,
        "overdue": overdue_tasks,
        "critical": critical_tasks,
        "high_risk": high_risk_tasks
    }


@router.get("/priority")
async def get_priority_recommendation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get priority-based recommendation for what to work on next."""
    # Get all user's tasks
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    
    # Use scheduler to get recommendation
    scheduler = TaskScheduler()
    recommendation = scheduler.get_priority_recommendation(tasks)
    
    return recommendation


@router.get("/schedule/today")
async def get_todays_schedule(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    available_hours: float = 8.0
) -> Dict[str, Any]:
    """Get today's schedule."""
    # Get all user's tasks
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    
    # Use scheduler to get today's schedule
    scheduler = TaskScheduler()
    schedule = scheduler.get_todays_schedule(tasks, available_hours)
    
    return schedule


@router.get("/schedule/weekly")
async def get_weekly_schedule(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    available_hours_per_day: float = 8.0
) -> Dict[str, Any]:
    """Get weekly schedule."""
    # Get all user's tasks
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    
    # Use scheduler to get weekly schedule
    scheduler = TaskScheduler()
    schedule = scheduler.get_weekly_schedule(tasks, available_hours_per_day)
    
    return {
        "weekly_schedule": schedule
    }


@router.get("/workload")
async def get_workload_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get workload analysis and conflict detection."""
    # Get all user's tasks
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    
    # Use workload engine to analyze
    workload_engine = WorkloadEngine()
    analysis = workload_engine.detect_conflicts(tasks)
    
    return analysis


@router.get("/refresh")
async def refresh_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Refresh dashboard data (recalculate priorities)."""
    # Get all user's tasks
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    
    # Refresh priorities
    from backend.services.priority_engine import PriorityEngine
    from backend.services.risk_engine import RiskEngine
    
    for task in tasks:
        if task.status in ["Pending", "In Progress"]:
            task.priority_score = PriorityEngine.calculate_priority_score(
                deadline=task.deadline,
                importance=task.importance,
                estimated_duration_minutes=task.estimated_duration_minutes
            )
            task.risk_level = RiskEngine.calculate_risk_level(
                estimated_duration_minutes=task.estimated_duration_minutes,
                deadline=task.deadline
            )
            
            # Check for overdue
            if task.deadline < datetime.utcnow() and task.status not in ["Completed"]:
                task.status = "Overdue"
    
    db.commit()
    
    # Return updated summary
    return await get_dashboard_summary(current_user, db)
