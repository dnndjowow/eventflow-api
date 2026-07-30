from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
import jwt

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):

    data_copy = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    issued = datetime.now(timezone.utc)
    type = "access"
    data_copy.update({'exp': expire, 'iat': issued, 'type': type})
    return jwt.encode(data_copy, SECRET_KEY, algorithm=ALGORITHM)

