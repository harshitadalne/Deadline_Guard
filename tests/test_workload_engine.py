import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import pytest
from backend.services.workload_engine import WorkloadEngine
from backend.models.task import Task


class TestWorkloadEngine:
    """Test suite for WorkloadEngine."""
    
    def test_calculate_total_workload_empty(self):
        """Test workload calculation with no tasks."""
        workload = WorkloadEngine.calculate_total_workload([])
        assert workload["total_tasks"] == 0
        assert workload["total_work_hours"] == 0.0
        assert workload["deficit_hours"] == 0.0
    
    def test_calculate_total_workload_sufficient_time(self):
        """Test workload calculation when sufficient time is available."""
        tasks = [
            Task(
                id=1,
                user_id=1,
                title="Task 1",
                description="",
                category="Academic",
                deadline=datetime.utcnow() + timedelta(hours=10),
                estimated_duration_minutes=120,  # 2 hours
                importance="Medium",
                difficulty="Medium",
                status="Pending",
                priority_score=50.0,
                risk_level="LOW"
            )
        ]
        
        workload = WorkloadEngine.calculate_total_workload(tasks)
        assert workload["total_tasks"] == 1
        assert workload["total_work_hours"] == 2.0
        assert workload["surplus_hours"] > 0
        assert workload["deficit_hours"] == 0.0
    
    def test_calculate_total_workload_insufficient_time(self):
        """Test workload calculation when insufficient time is available."""
        tasks = [
            Task(
                id=1,
                user_id=1,
                title="Task 1",
                description="",
                category="Academic",
                deadline=datetime.utcnow() + timedelta(hours=2),
                estimated_duration_minutes=240,  # 4 hours
                importance="High",
                difficulty="Medium",
                status="Pending",
                priority_score=80.0,
                risk_level="CRITICAL"
            )
        ]
        
        workload = WorkloadEngine.calculate_total_workload(tasks)
        assert workload["total_tasks"] == 1
        assert workload["total_work_hours"] == 4.0
        assert workload["deficit_hours"] > 0
        assert workload["surplus_hours"] == 0.0
    
    def test_detect_conflicts_no_conflict(self):
        """Test conflict detection when no conflicts exist."""
        tasks = [
            Task(
                id=1,
                user_id=1,
                title="Task 1",
                description="",
                category="Academic",
                deadline=datetime.utcnow() + timedelta(hours=10),
                estimated_duration_minutes=120,
                importance="Medium",
                difficulty="Medium",
                status="Pending",
                priority_score=50.0,
                risk_level="LOW"
            )
        ]
        
        conflicts = WorkloadEngine.detect_conflicts(tasks, available_hours_per_day=8)
        assert conflicts["has_conflict"] == False
        assert conflicts["conflict_type"] is None
    
    def test_detect_conflicts_with_conflict(self):
        """Test conflict detection when conflicts exist."""
        tasks = [
            Task(
                id=1,
                user_id=1,
                title="Task 1",
                description="",
                category="Academic",
                deadline=datetime.utcnow() + timedelta(hours=24),
                estimated_duration_minutes=600,  # 10 hours
                importance="High",
                difficulty="Medium",
                status="Pending",
                priority_score=80.0,
                risk_level="HIGH"
            )
        ]
        
        conflicts = WorkloadEngine.detect_conflicts(tasks, available_hours_per_day=8)
        assert conflicts["has_conflict"] == True
        assert conflicts["conflict_type"] == "SINGLE_DAY"
        assert len(conflicts["conflicting_days"]) > 0
    
    def test_get_daily_schedule(self):
        """Test daily schedule generation."""
        tasks = [
            Task(
                id=1,
                user_id=1,
                title="Task 1",
                description="",
                category="Academic",
                deadline=datetime.utcnow() + timedelta(hours=24),
                estimated_duration_minutes=120,
                importance="Medium",
                difficulty="Medium",
                status="Pending",
                priority_score=50.0,
                risk_level="LOW"
            )
        ]
        
        schedule = WorkloadEngine.get_daily_schedule(tasks, available_hours_per_day=8, days_to_plan=3)
        
        assert len(schedule) == 3
        assert schedule[0]["date"] is not None
        assert schedule[0]["available_hours"] == 8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
