from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserResponse
from app.dependency import get_current_user
from app.database import get_async_db
from app.auth import hash_password, verify_password, create_access_token
from app.schemas.auth import AuthResponse


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


@router.post('/token', response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def create_token(user_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(get_async_db)]):

    get_user = await db.scalar(select(UserModel).where(
        UserModel.username == user_data.username,
        UserModel.is_active == True
    )
)
    
    if get_user is None:
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    
    password_check = verify_password(user_data.password, get_user.hashed_password)

    if not password_check:
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    
    access_token = create_access_token(data={'sub': str(get_user.id)})

    return {
    "access_token": access_token,
    "token_type": "bearer",
}

@router.get('/me', response_model=UserResponse)
async def get_curr_user(user: Annotated[UserModel, Depends(get_current_user)]):

    return user