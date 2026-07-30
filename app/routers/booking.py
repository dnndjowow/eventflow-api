from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from datetime import datetime

from app.database import get_async_db
from app.models.booking import Booking as BookingModel
from app.models.event import Event as EventModel
from app.models.user import User as UserModel
from app.schemas.booking import BookingCreate, BookingResponse, BookingStatusPatch
from app.dependency import get_current_user, RoleCheck


router = APIRouter(
    prefix='/bookings',
    tags=['bookings']
)


@router.post('/', response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(booking: BookingCreate, user: Annotated[UserModel, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_async_db)]):

    event_check = await db.scalar(select(EventModel).where(
        EventModel.id == booking.event_id,
        EventModel.is_active == True
    ))

    if event_check is None:
        raise HTTPException(
            status_code=404
        )
    
    if event_check.booking_deadline <= datetime.now():
        raise HTTPException(
            status_code=409
        )
    
    if event_check.available_seats < booking.seats:
        raise HTTPException(
            status_code=409
        )
    
    booking_check = await db.scalar(select(BookingModel).where(
        BookingModel.user_id == user.id,
        BookingModel.event_id == booking.event_id,
        BookingModel.status.in_(['pending', 'confirmed', 'checked_in'])
    ))

    if booking_check is not None:
        raise HTTPException(
            status_code=409
        )
    total_amount_price = event_check.price * booking.seats

    new_booking = BookingModel(
        **booking.model_dump(),
        user_id=user.id,
        unit_price=event_check.price,
        total_amount=total_amount_price,
        status='pending'
    )

    event_check.available_seats -= new_booking.seats

    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)
    return new_booking


@router.get('/me', response_model=list[BookingResponse])
async def get_booking_current_user(db: Annotated[AsyncSession, Depends(get_async_db)], user: Annotated[UserModel, Depends(get_current_user)]):
    return (await db.scalars(select(BookingModel).where(
        BookingModel.user_id == user.id
    ))).all()


@router.get('/', response_model=list[BookingResponse], dependencies=[Depends(RoleCheck(correct_role=['admin', 'manager']))])
async def get_all_bookings(db: Annotated[AsyncSession, Depends(get_async_db)]):
    
    bookings = (await db.scalars(select(BookingModel))).all()
    return bookings


@router.get('/{booking_id}', response_model=BookingResponse)
async def get_booking(booking_id: int, db: Annotated[AsyncSession, Depends(get_async_db)], user: Annotated[UserModel, Depends(get_current_user)]):

    booking = await db.scalar(
        select(BookingModel).where(
            BookingModel.id == booking_id
        )
    )

    if booking is None:
        raise HTTPException(
            status_code=404
        )

    if (
        booking.user_id != user.id
        and user.role not in ["admin", "manager"]
    ):
        raise HTTPException(
            status_code=403
        )

    return booking


@router.patch('/{booking_id}/status', response_model=BookingResponse, status_code=status.HTTP_200_OK)
async def update_booking(
    booking_id: int,
    booking_status: BookingStatusPatch,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[UserModel, Depends(get_current_user)]
):
    
    correct_transitions = {
        "pending": ["confirmed", "cancelled"],
        "confirmed": ["checked_in", "cancelled"],
        "checked_in": ["completed"],
        "completed": [],
        "cancelled": [],
    }
    
    current_booking = await db.scalar(select(BookingModel).where(
        BookingModel.id == booking_id
    )
)

    if current_booking is None:
        raise HTTPException(
            status_code=404
        )
    
    is_staff = user.role in ["admin", "manager"]

    if current_booking.user_id != user.id and not is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
        )

    if not is_staff and booking_status.status != "cancelled":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT
        )

    allowed_statuses = correct_transitions[current_booking.status]

    if booking_status.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT
        )

    if booking_status.status == "cancelled":
        event = await db.scalar(
            select(EventModel).where(
                EventModel.id == current_booking.event_id,
                EventModel.is_active == True,
            )
        )

        if event is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND
            )

        if not is_staff and event.starts_at <= datetime.now():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT
            )

        event.available_seats += current_booking.seats

    current_booking.status = booking_status.status
    current_booking.updated_at = datetime.now()
    await db.commit()
    await db.refresh(current_booking)
    return current_booking
    

    

