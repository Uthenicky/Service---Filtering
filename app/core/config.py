from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  DATABASE_URL: str
  LLM_URL: str
  PROJECT_NAME: str = "Message Filtering Service"

  class Config:
    env_file = ".env"

settings = Settings()