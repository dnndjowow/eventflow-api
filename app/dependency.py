from fastapi import Depends, HTTPException, status, Header
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User as UserModel
from sqlalchemy import select

from app.database import get_async_db


x_cleint_list: list[dict] = []


def x_cleint_checker(x_client_id: Annotated[str | None, Header()] = None):

    if x_client_id is None:
        raise HTTPException(
            status_code=400
        )
    
    if len(x_client_id.strip()) < 3:
        raise HTTPException(
            status_code=400
        )
    
    x_cleint_list.append({'X-Client-Id': x_client_id})


async def check_x_token(db: Annotated[AsyncSession, Depends(get_async_db)], x_token: Annotated[str | None, Header()] = None) -> UserModel:

    current_user = await db.scalar(select(UserModel).where(
        UserModel.token == x_token
    ))

    if current_user is None:
        raise HTTPException(
            status_code=401
        )
    
    if current_user.is_active == False:
        raise HTTPException(
            status_code=403
        )
    
    return current_user



class RoleCheck:

    def __init__(self, correct_role: list[str]):
        self.correct_role = correct_role

    def __call__(self, current_user: Annotated[UserModel, Depends(check_x_token)]):

        if current_user.role not in self.correct_role:
            raise HTTPException(
                status_code=403
            )
        
        return current_user
