from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserResponse
from app.database import get_async_db
from app.auth import hash_password


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_async_db)]):

    username_check = await db.scalar(select(UserModel).where(
        UserModel.username == user.username
    )
)
    
    if username_check is not None:
        raise HTTPException(
            status_code=409
        )

    new_user = UserModel(username=user.username, hashed_password=hash_password(user.password), role='customer')

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user