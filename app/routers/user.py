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

@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_async_db)]):

    check_username = await db.scalar(select(UserModel).where(
        UserModel.username == user.username
    ))

    if check_username is not None:
        raise HTTPException(
            status_code=409
        )
    
    check_token = await db.scalar(select(UserModel).where(
        UserModel.token == user.token
    )) 

    if check_token is not None:
        raise HTTPException(
            status_code=409
        )
    
    new_user = UserModel(**user.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
    


@router.get('/me', response_model=UserResponse)
async def get_current_user(current_user: Annotated[UserModel, Depends(check_x_token)]):

    if current_user is None:
        raise HTTPException(
            status_code=404
        )
    
    return current_user
