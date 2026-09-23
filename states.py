from aiogram.fsm.state import State, StatesGroup

class CourseCreation(StatesGroup):
    waiting_for_duration = State()

class StudyState(StatesGroup):
    asking_question = State()