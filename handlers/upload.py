import io
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.parser import extract_text_from_file
from states import CourseCreation
from config import config

router = Router()

def get_duration_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="7 дней", callback_data="duration_7")],
        [InlineKeyboardButton(text="14 дней", callback_data="duration_14")],
        [InlineKeyboardButton(text="30 дней", callback_data="duration_30")]
    ])


@router.message(F.document)
async def handle_document(message: types.Message, state: FSMContext, bot: Bot):
    doc = message.document
    filename = doc.file_name
    
    
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ["pdf", "pptx", "ppt", "docx", "doc", "txt"]:
        await message.answer("Неподдерживаемый формат. Пришли PDF, PPTX, DOCX или TXT.")
        return

    msg = await message.answer("Скачиваю и читаю файл...")

    
    file_bytes_io = await bot.download(doc.file_id)
    file_bytes = file_bytes_io.read()

    
    text = await extract_text_from_file(file_bytes, filename)

    if not text or len(text) < 50:
        await msg.edit_text("Не удалось извлечь текст из файла или он слишком короткий.")
        return

    
    await state.update_data(raw_text=text, filename=filename)
    await state.set_state(CourseCreation.waiting_for_duration)

    
    user_info = f"@{message.from_user.username}" if message.from_user.username else f"ID {message.from_user.id}"
    await bot.send_message(
        config.ADMIN_ID,
        f"**Новый файл!**\nЮзер: {user_info}\nФайл: `{filename}` ({len(text)} символов)"
    )

    await msg.edit_text(
        f"Файл **{filename}** успешно прочитан!\n\n"
        "На сколько дней разбить обучение по этому материалу?",
        reply_markup=get_duration_keyboard()
    )