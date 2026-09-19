import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from datetime import datetime, timedelta
from typing import Dict, Any
from backend.services.priority_constants import (
    URGENCY_THRESHOLDS,
    DEFAULT_URGENCY_SCORE,
    IMPORTANCE_SCORES,
    PRIORITY_WEIGHTS
)


class PriorityEngine:
    """Engine for calculating task priority scores based on deterministic rules."""
    
    @staticmethod
    def calculate_urgency(deadline: datetime) -> float:
        """
        Calculate urgency score based on time remaining until deadline.
        
        Args:
            deadline: Task deadline datetime
            
        Returns:
            Urgency score (0-100)
        """
        now = datetime.utcnow()
        time_remaining = deadline - now
        
        # If deadline is in the past, maximum urgency
        if time_remaining.total_seconds() <= 0:
            return 100.0
        
        hours_remaining = time_remaining.total_seconds() / 3600
        
        # Find the appropriate urgency score based on thresholds
        urgency_score = DEFAULT_URGENCY_SCORE
        for threshold_hours, score in sorted(URGENCY_THRESHOLDS.items()):
            if hours_remaining <= threshold_hours:
                urgency_score = score
                break
        
        return float(urgency_score)
    
    @staticmethod
    def calculate_importance(importance: str) -> float:
        """
        Get importance score based on importance level.
        
        Args:
            importance: Importance level (Low, Medium, High, Critical)
            
        Returns:
            Importance score (0-100)
        """
        return float(IMPORTANCE_SCORES.get(importance, 50))
    
    @staticmethod
    def calculate_effort_pressure(
        estimated_duration_minutes: int,
        deadline: datetime
    ) -> float:
        """
        Calculate effort pressure based on estimated work vs available time.
        
        Args:
            estimated_duration_minutes: Estimated work duration in minutes
            deadline: Task deadline datetime
            
        Returns:
            Effort pressure score (0-100)
        """
        now = datetime.utcnow()
        time_remaining = deadline - now
        
        # If deadline is in the past, maximum pressure
        if time_remaining.total_seconds() <= 0:
            return 100.0
        
        available_minutes = time_remaining.total_seconds() / 60
        
        if available_minutes <= 0:
            return 100.0
        
        # Calculate pressure ratio
        pressure_ratio = estimated_duration_minutes / available_minutes
        
        # Normalize to 0-100 scale
        # If work equals available time, pressure = 100
        # If work is half of available time, pressure = 50
        pressure_score = min(pressure_ratio * 100, 100.0)
        
        return float(pressure_score)
    
    @staticmethod
    def calculate_priority_score(
        deadline: datetime,
        importance: str,
        estimated_duration_minutes: int
    ) -> float:
        """
        Calculate overall priority score using weighted formula.
        
        Formula:
        priority_score = 0.50 * urgency + 0.30 * importance + 0.20 * effort_pressure
        
        Args:
            deadline: Task deadline datetime
            importance: Importance level
            estimated_duration_minutes: Estimated work duration in minutes
            
        Returns:
            Priority score (0-100)
        """
        urgency = PriorityEngine.calculate_urgency(deadline)
        importance_score = PriorityEngine.calculate_importance(importance)
        effort_pressure = PriorityEngine.calculate_effort_pressure(
            estimated_duration_minutes, deadline
        )
        
        priority_score = (
            PRIORITY_WEIGHTS["urgency"] * urgency +
            PRIORITY_WEIGHTS["importance"] * importance_score +
            PRIORITY_WEIGHTS["effort_pressure"] * effort_pressure
        )
        
        return round(priority_score, 2)
    
    @staticmethod
    def explain_priority(
        deadline: datetime,
        importance: str,
        estimated_duration_minutes: int
    ) -> Dict[str, Any]:
        """
        Provide detailed explanation of priority calculation.
        
        Args:
            deadline: Task deadline datetime
            importance: Importance level
            estimated_duration_minutes: Estimated work duration in minutes
            
        Returns:
            Dictionary with detailed breakdown
        """
        urgency = PriorityEngine.calculate_urgency(deadline)
        importance_score = PriorityEngine.calculate_importance(importance)
        effort_pressure = PriorityEngine.calculate_effort_pressure(
            estimated_duration_minutes, deadline
        )
        
        priority_score = (
            PRIORITY_WEIGHTS["urgency"] * urgency +
            PRIORITY_WEIGHTS["importance"] * importance_score +
            PRIORITY_WEIGHTS["effort_pressure"] * effort_pressure
        )
        
        now = datetime.utcnow()
        time_remaining = deadline - now
        hours_remaining = time_remaining.total_seconds() / 3600
        
        return {
            "urgency": {
                "score": urgency,
                "hours_remaining": round(hours_remaining, 1),
                "explanation": f"Task is due in {round(hours_remaining, 1)} hours"
            },
            "importance": {
                "score": importance_score,
                "level": importance,
                "explanation": f"Task importance is {importance}"
            },
            "effort_pressure": {
                "score": effort_pressure,
                "estimated_hours": round(estimated_duration_minutes / 60, 1),
                "available_hours": round(hours_remaining, 1),
                "explanation": f"Requires {round(estimated_duration_minutes / 60, 1)} hours of work with {round(hours_remaining, 1)} hours available"
            },
            "final_priority": {
                "score": round(priority_score, 2),
                "formula": "0.50 * urgency + 0.30 * importance + 0.20 * effort_pressure"
            }
        }
