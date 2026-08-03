from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
import jwt

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):

    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    issued = datetime.now(timezone.utc)
    type = "access"
    payload.update({'exp': expire, 'iat': issued, 'type': type})
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)

def create_refresh_token(data: dict):

    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    issued = datetime.now(timezone.utc)
    payload.update({'exp': expire, 'iat': issued, 'type': 'refresh'})
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)
