import os
from pydantic import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    POSTGRES_URL: str
    WS_HOST: str
    WS_PORT: int
    SECRET_KEY: str
    DEBUG: bool
    BASE_DIR: Path = Path(
        __file__).absolute().parent

    class Config:
        env_file = '.env'
        extra = 'ignore'



settings = Settings(_env_file=os.getenv("ENV_FILE", ".env"))
