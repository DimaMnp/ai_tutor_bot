from datetime import datetime
from typing import Optional, List
from beanie import Document
from pydantic import BaseModel, Field
from .schemas import DayPlan


class StudyCourse(Document):
    user_id: int
    title: str
    raw_text: str
    duration_days: int
    days: List[DayPlan] = []
    current_day: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "study_courses"