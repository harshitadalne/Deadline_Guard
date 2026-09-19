import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import pytest
from backend.services.priority_engine import PriorityEngine


class TestPriorityEngine:
    """Test suite for PriorityEngine."""
    
    def test_calculate_urgency_critical(self):
        """Test urgency calculation for critical (<= 2 hours) deadline."""
        deadline = datetime.utcnow() + timedelta(hours=1)
        urgency = PriorityEngine.calculate_urgency(deadline)
        assert urgency == 100.0
    
    def test_calculate_urgency_very_soon(self):
        """Test urgency calculation for very soon (<= 6 hours) deadline."""
        deadline = datetime.utcnow() + timedelta(hours=4)
        urgency = PriorityEngine.calculate_urgency(deadline)
        assert urgency == 90.0
    
    def test_calculate_urgency_soon(self):
        """Test urgency calculation for soon (<= 12 hours) deadline."""
        deadline = datetime.utcnow() + timedelta(hours=10)
        urgency = PriorityEngine.calculate_urgency(deadline)
        assert urgency == 80.0
    
    def test_calculate_urgency_tomorrow(self):
        """Test urgency calculation for tomorrow (<= 24 hours) deadline."""
        deadline = datetime.utcnow() + timedelta(hours=20)
        urgency = PriorityEngine.calculate_urgency(deadline)
        assert urgency == 70.0
    
    def test_calculate_urgency_past_deadline(self):
        """Test urgency calculation for past deadline."""
        deadline = datetime.utcnow() - timedelta(hours=1)
        urgency = PriorityEngine.calculate_urgency(deadline)
        assert urgency == 100.0
    
    def test_calculate_importance_critical(self):
        """Test importance score for Critical level."""
        importance = PriorityEngine.calculate_importance("Critical")
        assert importance == 100.0
    
    def test_calculate_importance_high(self):
        """Test importance score for High level."""
        importance = PriorityEngine.calculate_importance("High")
        assert importance == 75.0
    
    def test_calculate_importance_medium(self):
        """Test importance score for Medium level."""
        importance = PriorityEngine.calculate_importance("Medium")
        assert importance == 50.0
    
    def test_calculate_importance_low(self):
        """Test importance score for Low level."""
        importance = PriorityEngine.calculate_importance("Low")
        assert importance == 25.0
    
    def test_calculate_effort_pressure_high(self):
        """Test effort pressure when work exceeds available time."""
        deadline = datetime.utcnow() + timedelta(hours=2)
        duration = 180  # 3 hours
        pressure = PriorityEngine.calculate_effort_pressure(duration, deadline)
        assert pressure == 100.0
    
    def test_calculate_effort_pressure_medium(self):
        """Test effort pressure when work is half of available time."""
        deadline = datetime.utcnow() + timedelta(hours=4)
        duration = 120  # 2 hours
        pressure = PriorityEngine.calculate_effort_pressure(duration, deadline)
        assert pressure == 50.0
    
    def test_calculate_effort_pressure_low(self):
        """Test effort pressure when work is much less than available time."""
        deadline = datetime.utcnow() + timedelta(hours=10)
        duration = 60  # 1 hour
        pressure = PriorityEngine.calculate_effort_pressure(duration, deadline)
        assert pressure == 10.0
    
    def test_calculate_priority_score(self):
        """Test overall priority score calculation."""
        deadline = datetime.utcnow() + timedelta(hours=4)
        importance = "High"
        duration = 120
        
        priority = PriorityEngine.calculate_priority_score(deadline, importance, duration)
        
        # Priority should be between 0 and 100
        assert 0 <= priority <= 100
        
        # High importance + soon deadline should give high priority
        assert priority > 50
    
    def test_explain_priority(self):
        """Test priority explanation generation."""
        deadline = datetime.utcnow() + timedelta(hours=4)
        importance = "High"
        duration = 120
        
        explanation = PriorityEngine.explain_priority(deadline, importance, duration)
        
        assert "urgency" in explanation
        assert "importance" in explanation
        assert "effort_pressure" in explanation
        assert "final_priority" in explanation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
