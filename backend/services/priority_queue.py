import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

import heapq
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.models.task import Task
from backend.services.priority_engine import PriorityEngine
from backend.services.risk_engine import RiskEngine


class DeadlinePriorityQueue:
    """
    Priority Queue implementation for task management using heapq.
    
    Tasks are ordered by priority score (highest first). Since heapq is a min-heap,
    we store negative priority scores to get max-heap behavior.
    """
    
    def __init__(self):
        """Initialize an empty priority queue."""
        self.heap = []
        self.task_map = {}  # Map task_id to task data for quick lookup
        self.counter = 0  # For tie-breaking
    
    def add_task(self, task: Task) -> None:
        """
        Add a task to the priority queue.
        
        Args:
            task: Task object to add
        """
        # Recalculate priority to ensure it's current
        priority_score = PriorityEngine.calculate_priority_score(
            deadline=task.deadline,
            importance=task.importance,
            estimated_duration_minutes=task.estimated_duration_minutes
        )
        
        # Use negative score for max-heap behavior (heapq is min-heap)
        # Include counter for tie-breaking to ensure FIFO order for equal priorities
        entry = (-priority_score, self.counter, task.id, task)
        heapq.heappush(self.heap, entry)
        self.task_map[task.id] = task
        self.counter += 1
    
    def remove_task(self, task_id: int) -> bool:
        """
        Remove a task from the priority queue.
        
        Args:
            task_id: ID of task to remove
            
        Returns:
            True if task was removed, False if not found
        """
        if task_id not in self.task_map:
            return False
        
        del self.task_map[task_id]
        
        # Rebuild heap without the removed task
        self.rebuild_queue()
        
        return True
    
    def rebuild_queue(self, tasks: Optional[List[Task]] = None) -> None:
        """
        Rebuild the priority queue from scratch.
        
        Args:
            tasks: Optional list of tasks to rebuild from. If None, uses task_map.
        """
        if tasks is not None:
            self.heap = []
            self.task_map = {}
            self.counter = 0
            for task in tasks:
                self.add_task(task)
        else:
            # Rebuild from existing task_map
            tasks_list = list(self.task_map.values())
            self.heap = []
            self.counter = 0
            for task in tasks_list:
                self.add_task(task)
    
    def get_highest_priority_task(self) -> Optional[Task]:
        """
        Get the task with the highest priority.
        
        Returns:
            Task object with highest priority, or None if queue is empty
        """
        while self.heap:
            priority_score, counter, task_id, task = heapq.heappop(self.heap)
            
            # Check if task is still in the map (not removed)
            if task_id in self.task_map:
                # Put it back since we just peeked
                heapq.heappush(self.heap, (priority_score, counter, task_id, task))
                return task
            else:
                # Task was removed, continue to next
                continue
        
        return None
    
    def get_top_n_tasks(self, n: int) -> List[Task]:
        """
        Get the top N tasks by priority.
        
        Args:
            n: Number of tasks to return
            
        Returns:
            List of top N tasks ordered by priority (highest first)
        """
        if n <= 0:
            return []
        
        # Get all valid tasks from heap
        valid_entries = []
        temp_heap = []
        
        while self.heap:
            entry = heapq.heappop(self.heap)
            priority_score, counter, task_id, task = entry
            
            if task_id in self.task_map:
                valid_entries.append(entry)
                temp_heap.append(entry)
        
        # Put everything back
        for entry in temp_heap:
            heapq.heappush(self.heap, entry)
        
        # Sort by priority (already sorted due to heap property)
        valid_entries.sort()  # Sorts by negative priority, so highest first
        
        # Extract tasks
        top_tasks = []
        for entry in valid_entries[:n]:
            _, _, _, task = entry
            top_tasks.append(task)
        
        return top_tasks
    
    def recalculate_priorities(self) -> None:
        """
        Recalculate all task priorities based on current time.
        This should be called periodically to update priorities as time passes.
        """
        # Rebuild queue with updated priorities
        tasks = list(self.task_map.values())
        self.rebuild_queue(tasks)
    
    def get_queue_size(self) -> int:
        """Get the number of tasks in the queue."""
        return len(self.task_map)
    
    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self.task_map) == 0
    
    def get_priority_explanation(self, task: Task) -> Dict[str, Any]:
        """
        Get detailed explanation of why a task has its current priority.
        
        Args:
            task: Task to analyze
            
        Returns:
            Dictionary with priority breakdown
        """
        return PriorityEngine.explain_priority(
            deadline=task.deadline,
            importance=task.importance,
            estimated_duration_minutes=task.estimated_duration_minutes
        )
    
    def get_risk_explanation(self, task: Task) -> Dict[str, Any]:
        """
        Get detailed explanation of a task's risk level.
        
        Args:
            task: Task to analyze
            
        Returns:
            Dictionary with risk breakdown
        """
        return RiskEngine.explain_risk(
            estimated_duration_minutes=task.estimated_duration_minutes,
            deadline=task.deadline
        )
