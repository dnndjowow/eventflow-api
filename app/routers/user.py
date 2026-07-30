from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserResponse
from app.database import get_async_db
from app.dependency import check_x_token


router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.get('/me', response_model=UserResponse)
async def get_current_user(current_user: Annotated[UserModel, Depends(check_x_token)]):

    if current_user is None:
        raise HTTPException(
            status_code=404
        )
    
    return current_user
