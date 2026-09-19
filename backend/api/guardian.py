import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from backend.database.database import get_db
from backend.models.task import Task
from backend.models.user import User
from backend.api.auth import get_current_user
from backend.services.llm_service import LLMService
from backend.services.scheduler import TaskScheduler
from backend.schemas.guardian import (
    GuardianChatRequest,
    GuardianChatResponse,
    TaskParseRequest,
    TaskParseResponse,
    ParsedTask,
    RecommendationRequest,
    RecommendationResponse
)

router = APIRouter()

# Initialize LLM service
llm_service = LLMService()


@router.post("/parse-task", response_model=TaskParseResponse)
async def parse_task_from_natural_language(
    request: TaskParseRequest,
    current_user: User = Depends(get_current_user)
) -> TaskParseResponse:
    """Parse task information from natural language input."""
    if not llm_service.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="LLM service is not available. Please check your API configuration."
        )
    
    parsed_data = llm_service.parse_task_from_natural_language(request.natural_language)
    
    if not parsed_data:
        raise HTTPException(
            status_code=400,
            detail="Failed to parse task from natural language. Please try again with a clearer description."
        )
    
    return TaskParseResponse(
        parsed_task=ParsedTask(**parsed_data),
        confidence=0.85  # Placeholder confidence score
    )


@router.post("/recommendation", response_model=RecommendationResponse)
async def get_guardian_recommendation(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> RecommendationResponse:
    """Get AI-powered recommendation with explanation."""
    # Get user's tasks
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    
    # Use scheduler to get algorithmic recommendation
    scheduler = TaskScheduler()
    algorithmic_rec = scheduler.get_priority_recommendation(tasks)
    
    # Generate AI explanation if available
    if algorithmic_rec.get("next_task") and llm_service.is_enabled():
        next_task = algorithmic_rec["next_task"]
        explanation = llm_service.explain_recommendation(
            task_data=next_task,
            analysis=algorithmic_rec.get("analysis", {})
        )
    else:
        explanation = algorithmic_rec.get("recommendation", "No recommendation available.")
    
    return RecommendationResponse(
        next_task=algorithmic_rec.get("next_task"),
        analysis=algorithmic_rec.get("analysis", {}),
        explanation=explanation
    )


@router.post("/chat", response_model=GuardianChatResponse)
async def chat_with_guardian(
    request: GuardianChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> GuardianChatResponse:
    """Chat with the Deadline Guardian AI assistant."""
    if not llm_service.is_enabled():
        return GuardianChatResponse(
            response="AI features are currently unavailable. Please check your API configuration in the .env file.",
            analysis=None
        )
    
    # Get user's tasks for context
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    
    # Build context for the LLM
    context = {
        "user": current_user.email,
        "total_tasks": len(tasks),
        "pending_tasks": len([t for t in tasks if t.status in ["Pending", "In Progress"]]),
        "completed_tasks": len([t for t in tasks if t.status == "Completed"]),
        "tasks": [
            {
                "title": t.title,
                "status": t.status,
                "deadline": t.deadline.isoformat(),
                "priority_score": t.priority_score,
                "risk_level": t.risk_level,
                "importance": t.importance,
                "estimated_hours": round(t.estimated_duration_minutes / 60, 1)
            }
            for t in tasks[:10]  # Limit to 10 most relevant tasks
        ]
    }
    
    # Get AI response
    response = llm_service.answer_question(request.message, context)
    
    return GuardianChatResponse(
        response=response,
        analysis=context
    )


@router.post("/decompose-task")
async def decompose_task(
    task_title: str,
    task_description: str = "",
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Decompose a complex task into smaller subtasks."""
    if not llm_service.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="LLM service is not available. Please check your API configuration."
        )
    
    subtasks = llm_service.decompose_task(task_title, task_description)
    
    if not subtasks:
        raise HTTPException(
            status_code=400,
            detail="Failed to decompose task. Please try with a more specific task description."
        )
    
    return {
        "original_task": task_title,
        "subtasks": subtasks,
        "total_subtasks": len(subtasks)
    }
