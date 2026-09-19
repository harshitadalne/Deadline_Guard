import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from datetime import datetime
from typing import Dict, Any
from backend.services.priority_constants import RISK_THRESHOLDS


class RiskEngine:
    """Engine for calculating task risk levels based on deterministic rules."""
    
    @staticmethod
    def calculate_risk_level(
        estimated_duration_minutes: int,
        deadline: datetime
    ) -> str:
        """
        Calculate risk level based on estimated work vs available time.
        
        Risk Levels:
        - LOW: Work is <= 50% of available time
        - MEDIUM: Work is <= 80% of available time
        - HIGH: Work is <= 100% of available time
        - CRITICAL: Work exceeds available time
        
        Args:
            estimated_duration_minutes: Estimated work duration in minutes
            deadline: Task deadline datetime
            
        Returns:
            Risk level (LOW, MEDIUM, HIGH, CRITICAL)
        """
        now = datetime.utcnow()
        time_remaining = deadline - now
        
        # If deadline is in the past, critical risk
        if time_remaining.total_seconds() <= 0:
            return "CRITICAL"
        
        available_minutes = time_remaining.total_seconds() / 60
        
        if available_minutes <= 0:
            return "CRITICAL"
        
        # Calculate work ratio
        work_ratio = estimated_duration_minutes / available_minutes
        
        # Determine risk level based on thresholds
        if work_ratio <= RISK_THRESHOLDS["LOW"]:
            return "LOW"
        elif work_ratio <= RISK_THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        elif work_ratio <= RISK_THRESHOLDS["HIGH"]:
            return "HIGH"
        else:
            return "CRITICAL"
    
    @staticmethod
    def explain_risk(
        estimated_duration_minutes: int,
        deadline: datetime
    ) -> Dict[str, Any]:
        """
        Provide detailed explanation of risk calculation.
        
        Args:
            estimated_duration_minutes: Estimated work duration in minutes
            deadline: Task deadline datetime
            
        Returns:
            Dictionary with detailed breakdown
        """
        now = datetime.utcnow()
        time_remaining = deadline - now
        available_minutes = time_remaining.total_seconds() / 60
        available_hours = available_minutes / 60
        estimated_hours = estimated_duration_minutes / 60
        
        risk_level = RiskEngine.calculate_risk_level(
            estimated_duration_minutes, deadline
        )
        
        work_ratio = estimated_duration_minutes / available_minutes if available_minutes > 0 else float('inf')
        
        explanation = {
            "risk_level": risk_level,
            "estimated_work_hours": round(estimated_hours, 1),
            "available_time_hours": round(available_hours, 1),
            "work_ratio": round(work_ratio, 2),
            "time_deficit_hours": round(max(0, estimated_hours - available_hours), 1),
            "explanation": RiskEngine._get_risk_explanation(
                risk_level, estimated_hours, available_hours, work_ratio
            )
        }
        
        return explanation
    
    @staticmethod
    def _get_risk_explanation(
        risk_level: str,
        estimated_hours: float,
        available_hours: float,
        work_ratio: float
    ) -> str:
        """Generate human-readable risk explanation."""
        if risk_level == "LOW":
            return (f"✅ Low Risk: You have {round(available_hours, 1)} hours available "
                   f"for {round(estimated_hours, 1)} hours of work. "
                   f"Work is {round(work_ratio * 100, 0)}% of available time.")
        elif risk_level == "MEDIUM":
            return (f"⚠️ Medium Risk: You have {round(available_hours, 1)} hours available "
                   f"for {round(estimated_hours, 1)} hours of work. "
                   f"Work is {round(work_ratio * 100, 0)}% of available time. "
                   f"Start this task soon.")
        elif risk_level == "HIGH":
            return (f"🔶 High Risk: You have {round(available_hours, 1)} hours available "
                   f"for {round(estimated_hours, 1)} hours of work. "
                   f"Work is {round(work_ratio * 100, 0)}% of available time. "
                   f"Remaining time is close to estimated work.")
        else:  # CRITICAL
            deficit = round(estimated_hours - available_hours, 1)
            return (f"🔴 Critical Risk: Estimated work ({round(estimated_hours, 1)} hours) "
                   f"exceeds available time ({round(available_hours, 1)} hours) by {deficit} hours. "
                   f"Immediate action required.")
    
    @staticmethod
    def get_risk_emoji(risk_level: str) -> str:
        """Get emoji for risk level."""
        emoji_map = {
            "LOW": "🟢",
            "MEDIUM": "🟡",
            "HIGH": "🟠",
            "CRITICAL": "🔴"
        }
        return emoji_map.get(risk_level, "⚪")
