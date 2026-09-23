from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from states import CourseCreation, StudyState
from services.llm import generate_study_plan
from data.models import StudyCourse, DayPlan
from data.schemas import QuizItem

router = Router()

def get_day_keyboard(current_day: int, total_days: int):
    buttons = [
        [InlineKeyboardButton(text="Пройти тест", callback_data=f"quiz_{current_day}")],
        [InlineKeyboardButton(text="Задать вопрос ИИ", callback_data=f"ask_{current_day}")],
    ]
    nav_row = []
    if current_day > 1:
        nav_row.append(InlineKeyboardButton(text="Пред. день", callback_data=f"day_{current_day - 1}"))
    if current_day < total_days:
        nav_row.append(InlineKeyboardButton(text="Следующий день", callback_data=f"day_{current_day + 1}"))
    if nav_row:
        buttons.append(nav_row)
        
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(CourseCreation.waiting_for_duration, F.data.startswith("duration_"))
async def process_duration_selection(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    duration_days = int(call.data.split("_")[1])
    
    data = await state.get_data()
    raw_text = data.get("raw_text")
    filename = data.get("filename")

    await call.message.edit_text(f"**ИИ генерирует план на {duration_days} дней...**\n Это займет ~10-15 секунд.")

   
    llm_result = await generate_study_plan(raw_text, duration_days)

    
    days_list = []
    for d in llm_result.get("days", []):
        quiz_items = [QuizItem(**q) for q in d.get("quiz", [])]
        days_list.append(DayPlan(
            day_number=d["day_number"],
            title=d["title"],
            summary=d["summary"],
            quiz=quiz_items
        ))

    
    course = StudyCourse(
        user_id=call.from_user.id,
        title=llm_result.get("title", filename),
        raw_text=raw_text,
        duration_days=duration_days,
        days=days_list
    )
    await course.insert()
    await state.clear()

    
    day1 = course.days[0]
    text = f"**Курс: {course.title}**\n\n **{day1.title}**\n\n{day1.summary}"
    await call.message.edit_text(text, reply_markup=get_day_keyboard(1, course.duration_days))


@router.callback_query(F.data.startswith("day_"))
async def show_day(call: types.CallbackQuery):
    await call.answer()
    day_num = int(call.data.split("_")[1])
    
    course = await StudyCourse.find_one(
        StudyCourse.user_id == call.from_user.id
    )
    if not course:
        await call.message.answer("Курс не найден. Загрузи файл заново.")
        return

    day_data = course.days[day_num - 1]
    text = f"**Курс: {course.title}**\n\n **{day_data.title}**\n\n{day_data.summary}"
    await call.message.edit_text(text, reply_markup=get_day_keyboard(day_num, course.duration_days))


@router.callback_query(F.data.startswith("quiz_"))
async def start_quiz(call: types.CallbackQuery):
    await call.answer()
    day_num = int(call.data.split("_")[1])
    
    course = await StudyCourse.find_one(StudyCourse.user_id == call.from_user.id)
    day_data = course.days[day_num - 1]

    if not day_data.quiz:
        await call.message.answer("К сожалению, для этого дня нет вопросов.")
        return

    await call.message.answer(f" **Тест по теме: {day_data.title}**\n")
    for i, q in enumerate(day_data.quiz, 1):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=opt, callback_data=f"ans_{q.correct_option}_{idx}")]
            for idx, opt in enumerate(q.options)
        ])
        await call.message.answer(f"**Вопрос {i}:** {q.question}", reply_markup=kb)


@router.callback_query(F.data.startswith("ans_"))
async def process_answer(call: types.CallbackQuery):
    _, correct_idx, chosen_idx = call.data.split("_")
    
    if correct_idx == chosen_idx:
        await call.answer("Правильно!", show_alert=True)
        await call.message.edit_text(f"{call.message.text}\n\n **Ответ верный!**")
    else:
        await call.answer("Неверно!", show_alert=True)
        await call.message.edit_text(f"{call.message.text}\n\n **Неправильно, попробуй еще раз.**")