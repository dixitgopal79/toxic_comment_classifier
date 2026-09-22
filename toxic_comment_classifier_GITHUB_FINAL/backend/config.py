from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Toxic Comment Classifier"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db: str = "toxic_comment_db"
    model_path: str = "models/toxic_comment_model.keras"
    model_config_path: str = "models/model_config.json"
    api_key: str = ""
    rate_limit_per_minute: int = 60
    history_limit: int = 100
    cors_origins: str = "http://localhost:8000,http://127.0.0.1:8000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings():
    return Settings()
