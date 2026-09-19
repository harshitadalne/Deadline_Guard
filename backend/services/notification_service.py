import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.models.task import Task
from backend.models.notification import Notification
from backend.services.priority_constants import NOTIFICATION_TYPES


class NotificationService:
    """Service for generating and managing task notifications."""
    
    @staticmethod
    def generate_notifications(db: Session, user_id: int) -> List[Notification]:
        """
        Generate notifications for a user based on their tasks.
        
        Args:
            db: Database session
            user_id: User ID to generate notifications for
            
        Returns:
            List of generated notifications
        """
        # Get user's active tasks
        tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.status.in_(["Pending", "In Progress"])
        ).all()
        
        notifications = []
        now = datetime.utcnow()
        
        for task in tasks:
            time_until_deadline = task.deadline - now
            hours_until_deadline = time_until_deadline.total_seconds() / 3600
            
            # Generate notifications based on time remaining
            if hours_until_deadline < 0:
                # Task is overdue
                notification = Notification(
                    user_id=user_id,
                    task_id=task.id,
                    message=f"🚨 {task.title} is now overdue!",
                    notification_type="overdue",
                    is_read=False
                )
                notifications.append(notification)
                
            elif hours_until_deadline <= 1:
                # Due within 1 hour
                notification = Notification(
                    user_id=user_id,
                    task_id=task.id,
                    message=f"🔴 {task.title} is due in less than 1 hour!",
                    notification_type="deadline_soon",
                    is_read=False
                )
                notifications.append(notification)
                
            elif hours_until_deadline <= 6:
                # Due within 6 hours
                notification = Notification(
                    user_id=user_id,
                    task_id=task.id,
                    message=f"🟠 {task.title} is due in {round(hours_until_deadline, 1)} hours.",
                    notification_type="deadline_soon",
                    is_read=False
                )
                notifications.append(notification)
                
            elif hours_until_deadline <= 24:
                # Due within 24 hours (tomorrow)
                notification = Notification(
                    user_id=user_id,
                    task_id=task.id,
                    message=f"🟡 {task.title} is due tomorrow.",
                    notification_type="deadline_today",
                    is_read=False
                )
                notifications.append(notification)
            
            # Generate risk-based notifications
            if task.risk_level == "CRITICAL":
                notification = Notification(
                    user_id=user_id,
                    task_id=task.id,
                    message=f"🔴 {task.title} is at CRITICAL risk level!",
                    notification_type="risk_critical",
                    is_read=False
                )
                notifications.append(notification)
                
            elif task.risk_level == "HIGH":
                notification = Notification(
                    user_id=user_id,
                    task_id=task.id,
                    message=f"🟠 {task.title} is at HIGH risk level.",
                    notification_type="risk_high",
                    is_read=False
                )
                notifications.append(notification)
        
        # Save notifications to database
        for notification in notifications:
            # Check if similar notification already exists and is unread
            existing = db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.task_id == notification.task_id,
                Notification.notification_type == notification.notification_type,
                Notification.is_read == False
            ).first()
            
            if not existing:
                db.add(notification)
        
        db.commit()
        
        return notifications
    
    @staticmethod
    def get_unread_notifications(db: Session, user_id: int) -> List[Notification]:
        """
        Get all unread notifications for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of unread notifications
        """
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).order_by(Notification.created_at.desc()).all()
    
    @staticmethod
    def mark_as_read(db: Session, notification_id: int) -> bool:
        """
        Mark a notification as read.
        
        Args:
            db: Database session
            notification_id: Notification ID
            
        Returns:
            True if successful, False otherwise
        """
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            notification.is_read = True
            db.commit()
            return True
        return False
    
    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        """
        Mark all notifications for a user as read.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Number of notifications marked as read
        """
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        db.commit()
        return count
    
    @staticmethod
    def delete_old_notifications(db: Session, days_to_keep: int = 7) -> int:
        """
        Delete notifications older than specified days.
        
        Args:
            db: Database session
            days_to_keep: Number of days to keep notifications
            
        Returns:
            Number of notifications deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        count = db.query(Notification).filter(
            Notification.created_at < cutoff_date,
            Notification.is_read == True
        ).delete()
        db.commit()
        return count
