from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TMDB_API_KEY: str
    OMDB_API_KEY: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()