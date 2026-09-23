from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! \n" 
    " Я бот для создания индивидуальных учебных планов. \n"
    " Отправь мне текст или файл с материалом, и я помогу тебе составить план обучения.")