import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from backend.models.task import Task
from backend.services.priority_constants import DEFAULT_AVAILABLE_HOURS_PER_DAY


class WorkloadEngine:
    """Engine for calculating workload and detecting conflicts."""
    
    @staticmethod
    def calculate_total_workload(
        tasks: List[Task],
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate total workload for given tasks within a time period.
        
        Args:
            tasks: List of tasks to analyze
            end_time: Optional end time for calculation. If None, uses latest deadline.
            
        Returns:
            Dictionary with workload breakdown
        """
        if not tasks:
            return {
                "total_tasks": 0,
                "total_work_hours": 0.0,
                "total_available_hours": 0.0,
                "workload_ratio": 0.0,
                "deficit_hours": 0.0,
                "surplus_hours": 0.0
            }
        
        now = datetime.utcnow()
        
        # Filter only pending and in-progress tasks
        active_tasks = [t for t in tasks if t.status in ["Pending", "In Progress"]]
        
        if not active_tasks:
            return {
                "total_tasks": 0,
                "total_work_hours": 0.0,
                "total_available_hours": 0.0,
                "workload_ratio": 0.0,
                "deficit_hours": 0.0,
                "surplus_hours": 0.0
            }
        
        # Calculate total work required
        total_work_minutes = sum(task.estimated_duration_minutes for task in active_tasks)
        total_work_hours = total_work_minutes / 60
        
        # Calculate available time until latest deadline
        if end_time is None:
            end_time = max(task.deadline for task in active_tasks)
        
        available_time = end_time - now
        available_hours = max(available_time.total_seconds() / 3600, 0)
        
        # Calculate workload ratio
        workload_ratio = total_work_hours / available_hours if available_hours > 0 else float('inf')
        
        # Calculate deficit or surplus
        if total_work_hours > available_hours:
            deficit_hours = total_work_hours - available_hours
            surplus_hours = 0.0
        else:
            deficit_hours = 0.0
            surplus_hours = available_hours - total_work_hours
        
        return {
            "total_tasks": len(active_tasks),
            "total_work_hours": round(total_work_hours, 1),
            "total_available_hours": round(available_hours, 1),
            "workload_ratio": round(workload_ratio, 2),
            "deficit_hours": round(deficit_hours, 1),
            "surplus_hours": round(surplus_hours, 1)
        }
    
    @staticmethod
    def detect_conflicts(
        tasks: List[Task],
        available_hours_per_day: float = DEFAULT_AVAILABLE_HOURS_PER_DAY
    ) -> Dict[str, Any]:
        """
        Detect workload conflicts and identify problematic tasks.
        
        Args:
            tasks: List of tasks to analyze
            available_hours_per_day: Available working hours per day
            
        Returns:
            Dictionary with conflict analysis
        """
        if not tasks:
            return {
                "has_conflict": False,
                "conflict_type": None,
                "conflicting_tasks": [],
                "recommendation": "No tasks to analyze."
            }
        
        now = datetime.utcnow()
        
        # Filter active tasks
        active_tasks = [t for t in tasks if t.status in ["Pending", "In Progress"]]
        
        if not active_tasks:
            return {
                "has_conflict": False,
                "conflict_type": None,
                "conflicting_tasks": [],
                "recommendation": "No active tasks."
            }
        
        # Group tasks by day
        tasks_by_day = {}
        for task in active_tasks:
            days_until_deadline = (task.deadline - now).days
            if days_until_deadline < 0:
                days_until_deadline = 0  # Overdue tasks count as today
            
            if days_until_deadline not in tasks_by_day:
                tasks_by_day[days_until_deadline] = []
            tasks_by_day[days_until_deadline].append(task)
        
        # Check each day for conflicts
        conflicting_days = []
        all_conflicting_tasks = []
        
        for day_offset, day_tasks in tasks_by_day.items():
            day_work_hours = sum(task.estimated_duration_minutes / 60 for task in day_tasks)
            
            if day_work_hours > available_hours_per_day:
                conflicting_days.append({
                    "day_offset": day_offset,
                    "date": (now + timedelta(days=day_offset)).strftime("%Y-%m-%d"),
                    "work_hours": round(day_work_hours, 1),
                    "available_hours": available_hours_per_day,
                    "excess_hours": round(day_work_hours - available_hours_per_day, 1)
                })
                all_conflicting_tasks.extend(day_tasks)
        
        # Determine conflict type
        has_conflict = len(conflicting_days) > 0
        conflict_type = None
        recommendation = None
        
        if has_conflict:
            if len(conflicting_days) == 1:
                conflict_type = "SINGLE_DAY"
                recommendation = f"You have {len(conflicting_days)} day with workload conflict."
            else:
                conflict_type = "MULTIPLE_DAYS"
                recommendation = f"You have {len(conflicting_days)} days with workload conflicts."
            
            total_excess = sum(day["excess_hours"] for day in conflicting_days)
            recommendation += f" Total excess work: {round(total_excess, 1)} hours."
        else:
            recommendation = "No workload conflicts detected. Your schedule is manageable."
        
        return {
            "has_conflict": has_conflict,
            "conflict_type": conflict_type,
            "conflicting_days": conflicting_days,
            "conflicting_tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "deadline": task.deadline.isoformat(),
                    "estimated_hours": round(task.estimated_duration_minutes / 60, 1)
                }
                for task in all_conflicting_tasks
            ],
            "recommendation": recommendation
        }
    
    @staticmethod
    def get_daily_schedule(
        tasks: List[Task],
        available_hours_per_day: float = DEFAULT_AVAILABLE_HOURS_PER_DAY,
        days_to_plan: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Generate a daily schedule based on task priorities and deadlines.
        
        Args:
            tasks: List of tasks to schedule
            available_hours_per_day: Available working hours per day
            days_to_plan: Number of days to plan ahead
            
        Returns:
            List of daily schedules
        """
        now = datetime.utcnow()
        
        # Filter active tasks and sort by deadline
        active_tasks = [t for t in tasks if t.status in ["Pending", "In Progress"]]
        active_tasks.sort(key=lambda t: t.deadline)
        
        schedule = []
        remaining_tasks = active_tasks.copy()
        
        for day in range(days_to_plan):
            day_date = now + timedelta(days=day)
            day_end = day_date.replace(hour=23, minute=59, second=59)
            available_hours = available_hours_per_day
            used_hours = 0.0
            
            day_tasks = []
            
            # Assign tasks to this day based on deadline and priority
            for task in remaining_tasks[:]:  # Iterate over copy
                if task.deadline <= day_end:
                    task_hours = task.estimated_duration_minutes / 60
                    
                    if used_hours + task_hours <= available_hours:
                        day_tasks.append({
                            "task_id": task.id,
                            "title": task.title,
                            "estimated_hours": round(task_hours, 1),
                            "deadline": task.deadline.isoformat(),
                            "importance": task.importance
                        })
                        used_hours += task_hours
                        remaining_tasks.remove(task)
            
            schedule.append({
                "date": day_date.strftime("%Y-%m-%d"),
                "available_hours": available_hours,
                "used_hours": round(used_hours, 1),
                "remaining_hours": round(available_hours - used_hours, 1),
                "tasks": day_tasks
            })
        
        return schedule
