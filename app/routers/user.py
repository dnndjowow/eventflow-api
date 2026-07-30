from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserResponse


router = APIRouter(
    prefix='/users',
    tags=['users']
)
