"""
Seed script to generate realistic student task data for demonstration.
"""
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.database.database import SessionLocal, init_db
from backend.models.user import User
from backend.models.task import Task
from backend.services.priority_constants import TASK_CATEGORIES, IMPORTANCE_LEVELS, DIFFICULTY_LEVELS


def seed_database():
    """Seed the database with demo user and tasks."""
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check if demo user already exists
        existing_user = db.query(User).filter(User.email == "demo@student.edu").first()
        if existing_user:
            print("Demo user already exists. Skipping seed.")
            return
        
        # Create demo user with properly hashed password
        import bcrypt
        password_bytes = "demo123".encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        demo_user = User(
            name="Alex Student",
            email="demo@student.edu",
            password_hash=password_hash
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        
        # Create realistic demo tasks
        demo_tasks = [
            {
                "title": "DBMS Assignment",
                "description": "Complete the database normalization assignment with ER diagrams",
                "category": "Academic",
                "deadline": datetime.now() + timedelta(hours=25),
                "estimated_duration_minutes": 180,
                "importance": "High",
                "difficulty": "Medium",
                "status": "Pending"
            },
            {
                "title": "DSA Practice",
                "description": "Solve 5 medium-level array problems on LeetCode",
                "category": "DSA",
                "deadline": datetime.now() + timedelta(hours=48),
                "estimated_duration_minutes": 120,
                "importance": "High",
                "difficulty": "Medium",
                "status": "Pending"
            },
            {
                "title": "Machine Learning Project",
                "description": "Implement logistic regression for the classification task",
                "category": "Project",
                "deadline": datetime.now() + timedelta(days=5),
                "estimated_duration_minutes": 300,
                "importance": "High",
                "difficulty": "Hard",
                "status": "Pending"
            },
            {
                "title": "OS Assignment",
                "description": "Implement page replacement algorithm simulation",
                "category": "Academic",
                "deadline": datetime.now() + timedelta(days=3),
                "estimated_duration_minutes": 150,
                "importance": "Medium",
                "difficulty": "Medium",
                "status": "Pending"
            },
            {
                "title": "Technical Interview Preparation",
                "description": "Prepare for Google technical interview - focus on system design",
                "category": "Interview",
                "deadline": datetime.now() + timedelta(days=7),
                "estimated_duration_minutes": 240,
                "importance": "Critical",
                "difficulty": "Hard",
                "status": "Pending"
            },
            {
                "title": "Resume Update",
                "description": "Add recent project experience and update skills section",
                "category": "Application",
                "deadline": datetime.now() + timedelta(days=4),
                "estimated_duration_minutes": 60,
                "importance": "Medium",
                "difficulty": "Easy",
                "status": "Pending"
            },
            {
                "title": "Internship Application",
                "description": "Complete application for summer internship at tech company",
                "category": "Application",
                "deadline": datetime.now() + timedelta(days=2),
                "estimated_duration_minutes": 90,
                "importance": "High",
                "difficulty": "Medium",
                "status": "Pending"
            },
            {
                "title": "College Presentation",
                "description": "Prepare slides for group project presentation",
                "category": "Academic",
                "deadline": datetime.now() + timedelta(days=6),
                "estimated_duration_minutes": 120,
                "importance": "Medium",
                "difficulty": "Easy",
                "status": "Pending"
            },
            {
                "title": "Coding Test",
                "description": "Complete online coding assessment for job application",
                "category": "Interview",
                "deadline": datetime.now() + timedelta(hours=12),
                "estimated_duration_minutes": 90,
                "importance": "Critical",
                "difficulty": "Hard",
                "status": "Pending"
            },
            {
                "title": "Research Paper",
                "description": "Write literature review section for research paper",
                "category": "Academic",
                "deadline": datetime.now() + timedelta(days=10),
                "estimated_duration_minutes": 180,
                "importance": "Medium",
                "difficulty": "Medium",
                "status": "Pending"
            },
            {
                "title": "Gym Workout",
                "description": "Complete full body workout routine",
                "category": "Personal",
                "deadline": datetime.now() + timedelta(hours=6),
                "estimated_duration_minutes": 60,
                "importance": "Low",
                "difficulty": "Easy",
                "status": "Pending"
            },
            {
                "title": "Birthday Party",
                "description": "Attend friend's birthday celebration",
                "category": "Event",
                "deadline": datetime.now() + timedelta(days=1, hours=4),
                "estimated_duration_minutes": 180,
                "importance": "Medium",
                "difficulty": "Easy",
                "status": "Pending"
            }
        ]
        
        for task_data in demo_tasks:
            task = Task(user_id=demo_user.id, **task_data)
            db.add(task)
        
        db.commit()
        print(f"Successfully seeded database with demo user and {len(demo_tasks)} tasks.")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
