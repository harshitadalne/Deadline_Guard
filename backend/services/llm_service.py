import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import OpenAI
from backend.config import settings


class LLMService:
    """Service for LLM/NLP integration with OpenAI."""
    
    def __init__(self):
        """Initialize LLM service with API configuration."""
        self.client = None
        self.model = settings.LLM_MODEL
        self.enabled = False
        
        if settings.LLM_API_KEY:
            try:
                self.client = OpenAI(api_key=settings.LLM_API_KEY)
                self.enabled = True
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
    
    def is_enabled(self) -> bool:
        """Check if LLM service is enabled."""
        return self.enabled
    
    def parse_task_from_natural_language(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parse task information from natural language input.
        
        Args:
            text: Natural language description of a task
            
        Returns:
            Dictionary with parsed task information or None if parsing fails
        """
        if not self.enabled:
            return None
        
        prompt = f"""
        Extract task information from the following natural language description.
        Return the result as a JSON object with these exact keys:
        - title: string (task title)
        - deadline: string (ISO format datetime or relative time like "tomorrow 6pm")
        - estimated_duration_minutes: integer (estimated time in minutes)
        - importance: string (one of: Low, Medium, High, Critical)
        - category: string (one of: Academic, Project, DSA, Interview, Application, Personal, Event, Other)
        - description: string (optional, additional details)
        
        Input: {text}
        
        Return only the JSON object, no additional text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a task extraction assistant. Extract structured task information from natural language."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            try:
                parsed_data = json.loads(result_text)
                
                # Validate and normalize the data
                validated_data = self._validate_parsed_task(parsed_data)
                return validated_data
            except json.JSONDecodeError:
                print(f"Failed to parse LLM response as JSON: {result_text}")
                return None
                
        except Exception as e:
            print(f"Error parsing task from natural language: {e}")
            return None
    
    def _validate_parsed_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize parsed task data."""
        valid_categories = ["Academic", "Project", "DSA", "Interview", "Application", "Personal", "Event", "Other"]
        valid_importance = ["Low", "Medium", "High", "Critical"]
        
        # Set defaults for missing fields
        if "title" not in data or not data["title"]:
            data["title"] = "Untitled Task"
        
        if "category" not in data or data["category"] not in valid_categories:
            data["category"] = "Other"
        
        if "importance" not in data or data["importance"] not in valid_importance:
            data["importance"] = "Medium"
        
        if "estimated_duration_minutes" not in data or not isinstance(data["estimated_duration_minutes"], int):
            data["estimated_duration_minutes"] = 60
        
        if "deadline" not in data or not data["deadline"]:
            # Default to tomorrow
            from datetime import timedelta
            data["deadline"] = (datetime.utcnow() + timedelta(days=1)).isoformat()
        
        # Parse deadline if it's not in ISO format
        if not data["deadline"].startswith("20"):
            data["deadline"] = self._parse_relative_deadline(data["deadline"])
        
        if "description" not in data:
            data["description"] = ""
        
        return data
    
    def _parse_relative_deadline(self, deadline_str: str) -> str:
        """Parse relative deadline string to ISO format."""
        from datetime import timedelta
        deadline_str = deadline_str.lower().strip()
        
        now = datetime.utcnow()
        
        if "tomorrow" in deadline_str:
            target_date = now + timedelta(days=1)
        elif "today" in deadline_str:
            target_date = now
        elif "next week" in deadline_str:
            target_date = now + timedelta(weeks=1)
        else:
            # Default to tomorrow
            target_date = now + timedelta(days=1)
        
        # Try to extract time
        if "am" in deadline_str or "pm" in deadline_str:
            try:
                # Simple time parsing
                time_part = deadline_str.split()[-1]
                hour = int(time_part.replace("am", "").replace("pm", ""))
                if "pm" in deadline_str and hour != 12:
                    hour += 12
                elif "am" in deadline_str and hour == 12:
                    hour = 0
                target_date = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            except:
                target_date = target_date.replace(hour=17, minute=0, second=0, microsecond=0)  # Default 5 PM
        else:
            target_date = target_date.replace(hour=17, minute=0, second=0, microsecond=0)  # Default 5 PM
        
        return target_date.isoformat()
    
    def explain_recommendation(self, task_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        Generate human-readable explanation of algorithmic recommendation.
        
        Args:
            task_data: Task information
            analysis: Algorithmic analysis (priority breakdown, risk breakdown, etc.)
            
        Returns:
            Human-readable explanation
        """
        if not self.enabled:
            return self._generate_fallback_explanation(task_data, analysis)
        
        prompt = f"""
        Based on the following algorithmic analysis, explain why this task should be worked on next.
        Provide a clear, concise explanation suitable for a student.
        
        Task: {task_data.get('title', 'Unknown')}
        Priority Score: {task_data.get('priority_score', 0)}/100
        Risk Level: {task_data.get('risk_level', 'Unknown')}
        Deadline: {task_data.get('deadline', 'Unknown')}
        Estimated Work: {task_data.get('estimated_hours', 0)} hours
        Importance: {task_data.get('importance', 'Unknown')}
        
        Algorithmic Analysis:
        {analysis}
        
        Provide a clear explanation in 2-3 sentences. Focus on the most important factors.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful study assistant that explains task priorities."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating explanation: {e}")
            return self._generate_fallback_explanation(task_data, analysis)
    
    def _generate_fallback_explanation(self, task_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate fallback explanation without LLM."""
        priority_score = task_data.get('priority_score', 0)
        risk_level = task_data.get('risk_level', 'Unknown')
        importance = task_data.get('importance', 'Unknown')
        
        explanation = f"This task has a priority score of {priority_score:.1f}/100"
        
        if risk_level == "CRITICAL":
            explanation += " and is at critical risk due to limited time remaining."
        elif risk_level == "HIGH":
            explanation += " and is high risk."
        elif importance == "Critical":
            explanation += " with critical importance."
        else:
            explanation += "."
        
        return explanation
    
    def decompose_task(self, task_title: str, task_description: str = "") -> Optional[List[Dict[str, Any]]]:
        """
        Decompose a complex task into smaller subtasks.
        
        Args:
            task_title: Title of the task to decompose
            task_description: Optional description of the task
            
        Returns:
            List of subtask dictionaries or None if decomposition fails
        """
        if not self.enabled:
            return None
        
        prompt = f"""
        Break down the following task into 3-5 smaller, manageable subtasks.
        Return the result as a JSON array of objects with these keys:
        - title: string (subtask title)
        - estimated_duration_minutes: integer (estimated time for this subtask)
        
        Task: {task_title}
        Description: {task_description}
        
        Return only the JSON array, no additional text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a task planning assistant. Break down complex tasks into smaller subtasks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            import json
            try:
                subtasks = json.loads(result_text)
                
                # Validate subtasks
                validated_subtasks = []
                for subtask in subtasks:
                    if "title" in subtask and subtask["title"]:
                        validated_subtask = {
                            "title": subtask["title"],
                            "estimated_duration_minutes": subtask.get("estimated_duration_minutes", 30)
                        }
                        validated_subtasks.append(validated_subtask)
                
                return validated_subtasks if validated_subtasks else None
                
            except json.JSONDecodeError:
                print(f"Failed to parse LLM response as JSON: {result_text}")
                return None
                
        except Exception as e:
            print(f"Error decomposing task: {e}")
            return None
    
    def answer_question(self, question: str, context: Dict[str, Any]) -> str:
        """
        Answer a natural language question using provided context.
        
        Args:
            question: User's question
            context: Context data (tasks, priorities, etc.)
            
        Returns:
            Answer to the question
        """
        if not self.enabled:
            return "AI features are currently unavailable. Please check your API configuration."
        
        prompt = f"""
        Answer the following question based on the provided context about the user's tasks and schedule.
        Only use information from the context. Do not invent or assume information.
        
        Question: {question}
        
        Context:
        {context}
        
        Provide a helpful, concise answer. If the answer cannot be determined from the context, say so.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful study assistant that answers questions about tasks and deadlines."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error answering question: {e}")
            return "I'm sorry, I couldn't process your question at this time."
