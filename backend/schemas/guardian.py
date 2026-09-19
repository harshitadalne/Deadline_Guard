from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class GuardianChatRequest(BaseModel):
    message: str
    user_id: int


class GuardianChatResponse(BaseModel):
    response: str
    analysis: Optional[Dict[str, Any]] = None


class TaskParseRequest(BaseModel):
    natural_language: str
    user_id: int


class ParsedTask(BaseModel):
    title: str
    deadline: str
    estimated_duration_minutes: int
    importance: str
    category: str
    description: Optional[str] = None


class TaskParseResponse(BaseModel):
    parsed_task: ParsedTask
    confidence: float


class RecommendationRequest(BaseModel):
    user_id: int
    available_hours: Optional[float] = None


class RecommendationResponse(BaseModel):
    next_task: Dict[str, Any]
    analysis: Dict[str, Any]
    explanation: str
