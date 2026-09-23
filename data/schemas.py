from pydantic import BaseModel
from typing import List



class QuizItem(BaseModel):
    question: str
    options: List[str]
    correct_option: int | str
    explanation: str

class DayPlan(BaseModel):
    day_number: int
    title: str
    summary: str
    quiz: List[QuizItem] = []
    is_completed: bool = False

