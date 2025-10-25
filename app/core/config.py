from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  DATABASE_URL: str
  LLM_URL: str
  PROJECT_NAME: str 
  RABBITMQ_URL: str
  FILTERING_QUEUE: str
  BADWORDS_COUNT_MAX: int
  class Config:
    env_file = ".env"

settings = Settings()