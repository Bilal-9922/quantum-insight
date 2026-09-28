import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    app_name: str = os.getenv("APP_NAME", "QuantumInsight")
    ai_api_key: str = os.getenv("AI_API_KEY", "")
    ai_model: str = os.getenv("AI_MODEL", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./quantuminsight.db")
    cors_origins: list[str] = None

    def __post_init__(self):
        raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
        self.cors_origins = [x.strip() for x in raw.split(",") if x.strip()]

settings = Settings()
