from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@db:5432/clouddrive"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    AI_API_KEY: str = "sk-a2187d46cbf84304ad921427f9e83e23"
    AI_API_BASE: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    AI_MODEL: str = "qwen3.6-plus"
    AI_MODELS: str = '[{"id":"qwen3.6-plus","name":"Qwen 3.6 Plus","provider":"阿里百炼"},{"id":"qwen3.5-122b-a10b","name":"Qwen 3.5 122B","provider":"阿里百炼"},{"id":"qwen3.6-flash-2026-04-16","name":"Qwen 3.6 Flash","provider":"阿里百炼"},{"id":"MiniMax-M2.5","name":"MiniMax M2.5","provider":"阿里百炼"},{"id":"deepseek-v4-pro","name":"DeepSeek V4 Pro","provider":"阿里百炼"}]'
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def available_models(self) -> list:
        try:
            return json.loads(self.AI_MODELS)
        except:
            return [{"id": "qwen3.6-plus", "name": "Qwen 3.6 Plus", "provider": "阿里百炼"}]


def get_settings() -> Settings:
    return Settings()
