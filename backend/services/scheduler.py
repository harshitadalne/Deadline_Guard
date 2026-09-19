import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from backend.models.task import Task
from backend.services.priority_queue import DeadlinePriorityQueue
from backend.services.workload_engine import WorkloadEngine
from backend.services.priority_constants import DEFAULT_AVAILABLE_HOURS_PER_DAY


class TaskScheduler:
    """Scheduler for generating optimal task schedules based on priorities and deadlines."""
    
    def __init__(self):
        """Initialize the scheduler with a priority queue."""
        self.priority_queue = DeadlinePriorityQueue()
        self.workload_engine = WorkloadEngine()
    
    def build_schedule_from_tasks(self, tasks: List[Task]) -> None:
        """
        Build priority queue from a list of tasks.
        
        Args:
            tasks: List of tasks to schedule
        """
        # Filter only active tasks
        active_tasks = [t for t in tasks if t.status in ["Pending", "In Progress"]]
        
        # Build priority queue
        self.priority_queue.rebuild_queue(active_tasks)
    
    def get_next_task(self) -> Optional[Task]:
        """
        Get the next task to work on based on priority.
        
        Returns:
            Next task to work on, or None if no tasks available
        """
        return self.priority_queue.get_highest_priority_task()
    
    def get_todays_schedule(
        self,
        tasks: List[Task],
        available_hours: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate today's schedule based on priority and available time.
        
        Args:
            tasks: List of all tasks
            available_hours: Optional available hours for today
            
        Returns:
            Dictionary with today's schedule
        """
        if available_hours is None:
            available_hours = DEFAULT_AVAILABLE_HOURS_PER_DAY
        
        now = datetime.utcnow()
        end_of_day = now.replace(hour=23, minute=59, second=59)
        
        # Build priority queue
        self.build_schedule_from_tasks(tasks)
        
        # Get tasks due today or tomorrow
        schedule_tasks = []
        remaining_hours = available_hours
        
        top_tasks = self.priority_queue.get_top_n_tasks(20)  # Get top 20 tasks
        
        for task in top_tasks:
            if task.deadline <= end_of_day + timedelta(days=1):
                task_hours = task.estimated_duration_minutes / 60
                
                if remaining_hours >= task_hours:
                    schedule_tasks.append({
                        "task_id": task.id,
                        "title": task.title,
                        "start_time": None,  # Will be calculated
                        "end_time": None,    # Will be calculated
                        "duration_hours": round(task_hours, 1),
                        "priority_score": task.priority_score,
                        "risk_level": task.risk_level,
                        "deadline": task.deadline.isoformat()
                    })
                    remaining_hours -= task_hours
                else:
                    break  # No more time available
        
        # Calculate start/end times
        current_time = now
        for task in schedule_tasks:
            task["start_time"] = current_time.strftime("%I:%M %p")
            duration_hours = task["duration_hours"]
            current_time += timedelta(hours=duration_hours)
            task["end_time"] = current_time.strftime("%I:%M %p")
        
        return {
            "date": now.strftime("%Y-%m-%d"),
            "available_hours": available_hours,
            "scheduled_hours": round(available_hours - remaining_hours, 1),
            "remaining_hours": round(remaining_hours, 1),
            "tasks": schedule_tasks,
            "total_tasks_scheduled": len(schedule_tasks)
        }
    
    def get_weekly_schedule(
        self,
        tasks: List[Task],
        available_hours_per_day: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a weekly schedule.
        
        Args:
            tasks: List of all tasks
            available_hours_per_day: Optional available hours per day
            
        Returns:
            List of daily schedules for the week
        """
        if available_hours_per_day is None:
            available_hours_per_day = DEFAULT_AVAILABLE_HOURS_PER_DAY
        
        return self.workload_engine.get_daily_schedule(
            tasks=tasks,
            available_hours_per_day=available_hours_per_day,
            days_to_plan=7
        )
    
    def analyze_workload(self, tasks: List[Task]) -> Dict[str, Any]:
        """
        Analyze current workload and detect conflicts.
        
        Args:
            tasks: List of all tasks
            
        Returns:
            Dictionary with workload analysis
        """
        return self.workload_engine.detect_conflicts(tasks)
    
    def get_priority_recommendation(self, tasks: List[Task]) -> Dict[str, Any]:
        """
        Get priority-based recommendation for what to work on next.
        
        Args:
            tasks: List of all tasks
            
        Returns:
            Dictionary with recommendation
        """
        self.build_schedule_from_tasks(tasks)
        next_task = self.get_next_task()
        
        if not next_task:
            return {
                "recommendation": "No pending tasks. You're all caught up! 🎉",
                "next_task": None,
                "analysis": {
                    "total_pending": 0,
                    "workload_status": "CLEAR"
                }
            }
        
        # Get detailed analysis
        priority_explanation = self.priority_queue.get_priority_explanation(next_task)
        risk_explanation = self.priority_queue.get_risk_explanation(next_task)
        
        # Analyze overall workload
        workload_analysis = self.analyze_workload(tasks)
        
        return {
            "recommendation": f"Work on: {next_task.title}",
            "next_task": {
                "id": next_task.id,
                "title": next_task.title,
                "priority_score": next_task.priority_score,
                "risk_level": next_task.risk_level,
                "deadline": next_task.deadline.isoformat(),
                "estimated_hours": round(next_task.estimated_duration_minutes / 60, 1),
                "importance": next_task.importance
            },
            "analysis": {
                "priority_breakdown": priority_explanation,
                "risk_breakdown": risk_explanation,
                "workload_analysis": workload_analysis,
                "total_pending": len([t for t in tasks if t.status in ["Pending", "In Progress"]])
            }
        }
    
    def refresh_priorities(self, tasks: List[Task]) -> None:
        """
        Refresh all task priorities based on current time.
        
        Args:
            tasks: List of all tasks
        """
        self.build_schedule_from_tasks(tasks)
