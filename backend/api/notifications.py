import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database.database import get_db
from backend.models.notification import Notification
from backend.models.user import User
from backend.api.auth import get_current_user
from backend.services.notification_service import NotificationService

router = APIRouter()


@router.get("/")
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    unread_only: bool = False
) -> List[dict]:
    """Get notifications for the current user."""
    if unread_only:
        notifications = NotificationService.get_unread_notifications(db, current_user.id)
    else:
        notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id
        ).order_by(Notification.created_at.desc()).all()
    
    return [
        {
            "id": n.id,
            "message": n.message,
            "notification_type": n.notification_type,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
            "task_id": n.task_id
        }
        for n in notifications
    ]


@router.post("/generate")
async def generate_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Generate new notifications based on current task status."""
    notifications = NotificationService.generate_notifications(db, current_user.id)
    
    return {
        "message": f"Generated {len(notifications)} new notifications",
        "count": len(notifications)
    }


@router.post("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Mark a notification as read."""
    # Verify notification belongs to user
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        return {"error": "Notification not found"}
    
    success = NotificationService.mark_as_read(db, notification_id)
    
    if success:
        return {"message": "Notification marked as read"}
    else:
        return {"error": "Failed to mark notification as read"}


@router.post("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Mark all notifications as read."""
    count = NotificationService.mark_all_as_read(db, current_user.id)
    
    return {
        "message": f"Marked {count} notifications as read",
        "count": count
    }


@router.delete("/old")
async def delete_old_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days_to_keep: int = 7
) -> dict:
    """Delete old notifications."""
    count = NotificationService.delete_old_notifications(db, days_to_keep)
    
    return {
        "message": f"Deleted {count} old notifications",
        "count": count
    }
