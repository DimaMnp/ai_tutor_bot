from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN: str
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "ai_tutor_db"
    OPENAI_API_KEY: str
    ADMIN_ID: int
    OPENAI_BASE_URL: str = "https://api.proxyapi.ru/openai/v1"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

config = Settings()