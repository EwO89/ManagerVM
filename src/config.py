import os
from pydantic import BaseSettings, BaseModel
from pathlib import Path


BASE_DIR = Path(__file__).absolute().parent


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "private_key.pem"
    public_key_path: Path = BASE_DIR / "certs" / "public_key.pem"
    algorithm: str = 'RS256'


class Settings(BaseSettings):
    POSTGRES_URL: str
    WS_HOST: str
    WS_PORT: int
    SECRET_KEY: str
    DEBUG: bool
    auth_jwt: AuthJWT = AuthJWT()

    class Config:
        env_file = '.env'
        extra = 'ignore'


settings = Settings(_env_file=os.getenv("ENV_FILE", ".env"))
