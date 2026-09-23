from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from states import StudyState
from data.models import StudyCourse
from services.llm import ask_llm_question

router = Router()

@router.callback_query(F.data.startswith("ask_"))
async def prepare_question(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    day_num = int(call.data.split("_")[1])
    
    await state.update_data(current_day=day_num)
    await state.set_state(StudyState.asking_question)
    
    await call.message.answer(
        "**Задай любой вопрос по теории этого дня.**\n"
        "Напиши сообщение в чат, и ИИ поможет разобраться:"
    )

@router.message(StudyState.asking_question)
async def handle_user_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    day_num = data.get("current_day")

    course = await StudyCourse.find_one(StudyCourse.user_id == message.from_user.id)
    if not course:
        await message.answer("Ошибка контекста. Начни заново.")
        await state.clear()
        return

    day_data = course.days[day_num - 1]
    
    msg = await message.answer("ИИ думает над ответом...")
    answer = await ask_llm_question(day_data.summary, message.text)
    
    await msg.edit_text(f"**Ответ ИИ:**\n\n{answer}")
    await state.clear()