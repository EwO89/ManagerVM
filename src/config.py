from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).absolute().parent.parent


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "private_key.pem"
    public_key_path: Path = BASE_DIR / "certs" / "public_key.pem"
    algorithm: str = 'RS256'
    access_token_expire_minutes: int = 15


class Settings(BaseSettings):
    POSTGRES_URL: str
    WS_HOST: str
    WS_PORT: int
    SECRET_KEY: str
    DEBUG: bool
    BASE_DIR: Path = BASE_DIR
    auth_jwt: AuthJWT = AuthJWT()

    class Config:
        env_file = '.env'
        extra = 'ignore'


settings = Settings()
