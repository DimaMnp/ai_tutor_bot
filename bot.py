import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import config
from database import init_db
from handlers import start, upload, course, qa

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    await init_db()

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()

    
    dp.include_router(start.router)
    dp.include_router(upload.router)
    dp.include_router(course.router)
    dp.include_router(qa.router)

    try:
        await bot.send_message(config.ADMIN_ID, "**Бот запущен и готов к плейтесту!**")
    except Exception as e:
        logger.warning(f"Не удалось отправить сообщение админу: {e}")

    logger.info("Запуск Long Polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())