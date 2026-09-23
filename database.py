from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from config import config
from models import StudyCourse

async def init_db():
    client = AsyncIOMotorClient(config.MONGO_URI)
    await init_beanie(
        database=client[config.MONGO_DB_NAME],
        document_models=[StudyCourse]
    )
    