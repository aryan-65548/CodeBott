from pathlib import Path
from pydantic_settings import BaseSettings

# Points to code-review-agent/.env no matter where you run from
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    groq_api_key: str
    groq_model: str = "llama3-70b-8192"
    github_token: str
    github_webhook_secret: str
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    class Config:
        env_file = str(ENV_PATH)
        env_file_encoding = "utf-8"

settings = Settings()