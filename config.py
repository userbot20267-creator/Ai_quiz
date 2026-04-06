import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Bot Settings
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    OWNER_ID = int(os.getenv("OWNER_ID", "0"))

    # OpenRouter Settings
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "AI Quiz Bot")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "bot_database.db")

    # Other Settings
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
    API_SECRET_KEY = os.getenv("API_SECRET_KEY", "default_secret")
    RATE_LIMIT_MESSAGES = int(os.getenv("RATE_LIMIT_MESSAGES", "30"))
    RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
    MAX_AI_REQUESTS_PER_USER = int(os.getenv("MAX_AI_REQUESTS_PER_USER", "10"))
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ar")

    # Admins
    ADMINS = list(
        filter(
            None,
            [
                int(x.strip())
                for x in os.getenv("ADMINS", "").split(",")
                if x.strip()
            ],
        )
    )
    if OWNER_ID and OWNER_ID not in ADMINS:
        ADMINS.append(OWNER_ID)

    # Force Subscribe Channels
    FORCE_CHANNELS = list(
        filter(None, os.getenv("FORCE_CHANNELS", "").split(","))
    )


config = Config()