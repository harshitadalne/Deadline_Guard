import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import pytest
from backend.services.risk_engine import RiskEngine


class TestRiskEngine:
    """Test suite for RiskEngine."""
    
    def test_calculate_risk_low(self):
        """Test risk calculation for LOW risk (work <= 50% of available time)."""
        deadline = datetime.utcnow() + timedelta(hours=10)
        duration = 180  # 3 hours
        risk = RiskEngine.calculate_risk_level(duration, deadline)
        assert risk == "LOW"
    
    def test_calculate_risk_medium(self):
        """Test risk calculation for MEDIUM risk (work <= 80% of available time)."""
        deadline = datetime.utcnow() + timedelta(hours=5)
        duration = 240  # 4 hours
        risk = RiskEngine.calculate_risk_level(duration, deadline)
        assert risk == "MEDIUM"
    
    def test_calculate_risk_high(self):
        """Test risk calculation for HIGH risk (work <= 100% of available time)."""
        deadline = datetime.utcnow() + timedelta(hours=4)
        duration = 240  # 4 hours
        risk = RiskEngine.calculate_risk_level(duration, deadline)
        assert risk == "HIGH"
    
    def test_calculate_risk_critical(self):
        """Test risk calculation for CRITICAL risk (work exceeds available time)."""
        deadline = datetime.utcnow() + timedelta(hours=2)
        duration = 180  # 3 hours
        risk = RiskEngine.calculate_risk_level(duration, deadline)
        assert risk == "CRITICAL"
    
    def test_calculate_risk_past_deadline(self):
        """Test risk calculation for past deadline."""
        deadline = datetime.utcnow() - timedelta(hours=1)
        duration = 60
        risk = RiskEngine.calculate_risk_level(duration, deadline)
        assert risk == "CRITICAL"
    
    def test_explain_risk_low(self):
        """Test risk explanation for LOW risk."""
        deadline = datetime.utcnow() + timedelta(hours=10)
        duration = 180
        
        explanation = RiskEngine.explain_risk(duration, deadline)
        
        assert explanation["risk_level"] == "LOW"
        assert "explanation" in explanation
        assert "Low Risk" in explanation["explanation"]
    
    def test_explain_risk_critical(self):
        """Test risk explanation for CRITICAL risk."""
        deadline = datetime.utcnow() + timedelta(hours=2)
        duration = 180
        
        explanation = RiskEngine.explain_risk(duration, deadline)
        
        assert explanation["risk_level"] == "CRITICAL"
        assert "explanation" in explanation
        assert "Critical Risk" in explanation["explanation"]
        assert explanation["time_deficit_hours"] > 0
    
    def test_get_risk_emoji(self):
        """Test risk emoji mapping."""
        assert RiskEngine.get_risk_emoji("LOW") == "🟢"
        assert RiskEngine.get_risk_emoji("MEDIUM") == "🟡"
        assert RiskEngine.get_risk_emoji("HIGH") == "🟠"
        assert RiskEngine.get_risk_emoji("CRITICAL") == "🔴"
        assert RiskEngine.get_risk_emoji("UNKNOWN") == "⚪"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
