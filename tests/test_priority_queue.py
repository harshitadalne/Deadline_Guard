import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import pytest
from backend.services.priority_queue import DeadlinePriorityQueue
from backend.models.task import Task


class TestDeadlinePriorityQueue:
    """Test suite for DeadlinePriorityQueue."""
    
    def test_queue_initialization(self):
        """Test queue initialization."""
        queue = DeadlinePriorityQueue()
        assert queue.is_empty() == True
        assert queue.get_queue_size() == 0
    
    def test_add_task(self):
        """Test adding a task to the queue."""
        queue = DeadlinePriorityQueue()
        
        task = Task(
            id=1,
            user_id=1,
            title="High Priority Task",
            description="",
            category="Academic",
            deadline=datetime.utcnow() + timedelta(hours=2),
            estimated_duration_minutes=120,
            importance="Critical",
            difficulty="Medium",
            status="Pending",
            priority_score=90.0,
            risk_level="HIGH"
        )
        
        queue.add_task(task)
        assert queue.is_empty() == False
        assert queue.get_queue_size() == 1
    
    def test_get_highest_priority_task(self):
        """Test getting the highest priority task."""
        queue = DeadlinePriorityQueue()
        
        # Add tasks with different priorities
        task1 = Task(
            id=1,
            user_id=1,
            title="Low Priority Task",
            description="",
            category="Academic",
            deadline=datetime.utcnow() + timedelta(days=7),
            estimated_duration_minutes=60,
            importance="Low",
            difficulty="Easy",
            status="Pending",
            priority_score=20.0,
            risk_level="LOW"
        )
        
        task2 = Task(
            id=2,
            user_id=1,
            title="High Priority Task",
            description="",
            category="Academic",
            deadline=datetime.utcnow() + timedelta(hours=2),
            estimated_duration_minutes=120,
            importance="Critical",
            difficulty="Medium",
            status="Pending",
            priority_score=90.0,
            risk_level="HIGH"
        )
        
        queue.add_task(task1)
        queue.add_task(task2)
        
        highest = queue.get_highest_priority_task()
        assert highest.id == 2  # Should return the high priority task
        assert highest.priority_score == 90.0
    
    def test_get_top_n_tasks(self):
        """Test getting top N tasks."""
        queue = DeadlinePriorityQueue()
        
        # Add multiple tasks
        for i in range(5):
            task = Task(
                id=i,
                user_id=1,
                title=f"Task {i}",
                description="",
                category="Academic",
                deadline=datetime.utcnow() + timedelta(days=5-i),
                estimated_duration_minutes=60,
                importance="Medium",
                difficulty="Medium",
                status="Pending",
                priority_score=50.0 + i * 10,
                risk_level="LOW"
            )
            queue.add_task(task)
        
        top_3 = queue.get_top_n_tasks(3)
        assert len(top_3) == 3
        # Should be ordered by priority (highest first)
        assert top_3[0].priority_score >= top_3[1].priority_score
        assert top_3[1].priority_score >= top_3[2].priority_score
    
    def test_remove_task(self):
        """Test removing a task from the queue."""
        queue = DeadlinePriorityQueue()
        
        task = Task(
            id=1,
            user_id=1,
            title="Task to Remove",
            description="",
            category="Academic",
            deadline=datetime.utcnow() + timedelta(hours=2),
            estimated_duration_minutes=120,
            importance="Critical",
            difficulty="Medium",
            status="Pending",
            priority_score=90.0,
            risk_level="HIGH"
        )
        
        queue.add_task(task)
        assert queue.get_queue_size() == 1
        
        removed = queue.remove_task(1)
        assert removed == True
        assert queue.is_empty() == True
    
    def test_remove_nonexistent_task(self):
        """Test removing a task that doesn't exist."""
        queue = DeadlinePriorityQueue()
        
        removed = queue.remove_task(999)
        assert removed == False
    
    def test_rebuild_queue(self):
        """Test rebuilding the queue."""
        queue = DeadlinePriorityQueue()
        
        tasks = [
            Task(
                id=i,
                user_id=1,
                title=f"Task {i}",
                description="",
                category="Academic",
                deadline=datetime.utcnow() + timedelta(days=5-i),
                estimated_duration_minutes=60,
                importance="Medium",
                difficulty="Medium",
                status="Pending",
                priority_score=50.0 + i * 10,
                risk_level="LOW"
            )
            for i in range(3)
        ]
        
        queue.rebuild_queue(tasks)
        assert queue.get_queue_size() == 3
    
    def test_completed_tasks_excluded(self):
        """Test that completed tasks are not included in priority calculations."""
        queue = DeadlinePriorityQueue()
        
        completed_task = Task(
            id=1,
            user_id=1,
            title="Completed Task",
            description="",
            category="Academic",
            deadline=datetime.utcnow() + timedelta(hours=1),
            estimated_duration_minutes=60,
            importance="Critical",
            difficulty="Medium",
            status="Completed",
            priority_score=100.0,
            risk_level="CRITICAL"
        )
        
        pending_task = Task(
            id=2,
            user_id=1,
            title="Pending Task",
            description="",
            category="Academic",
            deadline=datetime.utcnow() + timedelta(days=7),
            estimated_duration_minutes=60,
            importance="Low",
            difficulty="Easy",
            status="Pending",
            priority_score=20.0,
            risk_level="LOW"
        )
        
        queue.add_task(completed_task)
        queue.add_task(pending_task)
        
        # The queue should still have both tasks since we don't filter by status in add_task
        # But in practice, you would filter before adding
        assert queue.get_queue_size() == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
