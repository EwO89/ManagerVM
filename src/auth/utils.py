
import jwt
from src.config import settings
from datetime import datetime


def encode_jwt(payload: dict,
               private_key: str = settings.auth_jwt.private_key_path.read_text(),
               algorithm: str = settings.auth_jwt.algorithm
               ):
    to_encode = payload.copy()
    now = datetime.utcnow()
    to_encode.update(
        iat=now,
    )
    encoded = jwt.encode(
        payload,
        private_key,
        algorithm=algorithm
    )
    return encoded


def decode_jwt(
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm
):
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm])
    return decoded


