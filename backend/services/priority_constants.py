"""
Priority calculation constants and thresholds.
These values are used by the Priority Engine to calculate task priorities.
"""

# Urgency thresholds (in hours) and their corresponding scores
URGENCY_THRESHOLDS = {
    2: 100,    # <= 2 hours
    6: 90,     # <= 6 hours
    12: 80,    # <= 12 hours
    24: 70,    # <= 24 hours
    72: 50,    # <= 3 days (72 hours)
    168: 30,   # <= 7 days (168 hours)
}

# Default urgency score for tasks > 7 days
DEFAULT_URGENCY_SCORE = 10

# Importance scores
IMPORTANCE_SCORES = {
    "Low": 25,
    "Medium": 50,
    "High": 75,
    "Critical": 100,
}

# Priority calculation weights
PRIORITY_WEIGHTS = {
    "urgency": 0.50,
    "importance": 0.30,
    "effort_pressure": 0.20,
}

# Risk level thresholds (ratio of estimated work to available time)
RISK_THRESHOLDS = {
    "LOW": 0.5,        # Work is <= 50% of available time
    "MEDIUM": 0.8,     # Work is <= 80% of available time
    "HIGH": 1.0,       # Work is <= 100% of available time
    "CRITICAL": 1.0,   # Work exceeds available time
}

# Available hours per day for scheduling (default)
DEFAULT_AVAILABLE_HOURS_PER_DAY = 8

# Task categories
TASK_CATEGORIES = [
    "Academic",
    "Project",
    "DSA",
    "Interview",
    "Application",
    "Personal",
    "Event",
    "Other",
]

# Importance levels
IMPORTANCE_LEVELS = ["Low", "Medium", "High", "Critical"]

# Difficulty levels
DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

# Task statuses
TASK_STATUSES = ["Pending", "In Progress", "Completed", "Overdue"]

# Notification types
NOTIFICATION_TYPES = ["deadline_approaching", "deadline_today", "deadline_soon", "overdue", "risk_high", "risk_critical"]
