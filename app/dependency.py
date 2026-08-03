from fastapi import Depends, HTTPException, status, Header
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User as UserModel
from sqlalchemy import select
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timezone

from app.database import get_async_db
from app.config import SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


def decode_token(token: str, type_token: str):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("sub") is None:
            raise jwt.InvalidTokenError()

        if payload.get("type") != type_token:
            raise jwt.InvalidTokenError()
        
        int(payload.get("sub"))

        return payload
    
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"}
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_async_db)]):

    try:
        payload = decode_token(token, type_token='access')
        sub = int(payload['sub'])
    except (jwt.PyJWKError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            headers={'WWW-Authenticate': 'Bearer'}
        )

    current_user = await db.scalar(select(UserModel).where(
        UserModel.id == sub,
        UserModel.is_active == True
    )
)   
    if current_user is None:
        raise HTTPException(
            status_code=401,
            headers={'WWW-Authenticate': 'Bearer'}
        )
    
    return current_user
        

class RoleCheck:

    def __init__(self, correct_role: list[str]):
        self.correct_role = correct_role

    def __call__(self, current_user: Annotated[UserModel, Depends(get_current_user)]):

        if current_user.role not in self.correct_role:
            raise HTTPException(
                status_code=403
            )
        
        return current_user