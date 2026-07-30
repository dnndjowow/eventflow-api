from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.database import get_async_db
from app.models.event import Event as EventModel
from app.models.booking import Booking as BookingModel
from app.schemas.event import EventCreate, EventPatch, EventResponse
from app.dependency import get_current_user, RoleCheck


router = APIRouter(
    prefix='/events',
    tags=['events']
)

@router.post('/', response_model=EventResponse, status_code=status.HTTP_201_CREATED,dependencies=[Depends(RoleCheck(correct_role=['admin', 'manager']))])
async def create_event(event: EventCreate, db: Annotated[AsyncSession, Depends(get_async_db)]):
    
    new_event = EventModel(**event.model_dump(), available_seats=event.capacity)
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    return new_event


@router.get('/', response_model=list[EventResponse], dependencies=[Depends(get_current_user)])
async def get_all_event(db: Annotated[AsyncSession, Depends(get_async_db)]):

    events = (await db.scalars(select(EventModel).where(
        EventModel.is_active == True
    ))).all()

    return events

@router.get('/{event_id}', response_model=EventResponse, dependencies=[Depends(get_current_user)])
async def get_event(event_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]):

    event = await db.scalar(select(EventModel).where(
        EventModel.id == event_id,
        EventModel.is_active == True
    ))

    if event is None:
        raise HTTPException(
            status_code=404
        )
    
    return event


@router.patch('/{event_id}', response_model=EventResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(RoleCheck(correct_role=['admin', 'manager']))])
async def patch_event(event_id: int, event: EventPatch, db: Annotated[AsyncSession, Depends(get_async_db)]):

    get_event = await db.scalar(select(EventModel).where(
        EventModel.id == event_id,
        EventModel.is_active == True
    ))

    if get_event is None:
        raise HTTPException(
            status_code=404
        )
    
    if get_event.starts_at < datetime.now():
        raise HTTPException(
            status_code=400
        )
    
    update_event = event.model_dump(exclude_unset=True)
    old_event = {
        'title': get_event.title,
        'capacity': get_event.capacity,
        'price': get_event.price,
        'booking_deadline': get_event.booking_deadline,
        'starts_at': get_event.starts_at
    }

    if not update_event:
        raise HTTPException(
            status_code=400
        )
    
    event_after_update = old_event.copy()

    for key, value in update_event.items():
        event_after_update[key] = value

    
    if event_after_update['booking_deadline'] >= event_after_update['starts_at']:
        raise HTTPException(
            status_code=400
        )
    
    if event_after_update['starts_at'] < datetime.now():
        raise HTTPException(
            status_code=400
        )
    

    if event_after_update['capacity'] < (get_event.capacity - get_event.available_seats):
        raise HTTPException(
            status_code=400
        )

    new_available_seats = event_after_update['capacity'] - (get_event.capacity - get_event.available_seats)
    

    await db.execute(update(EventModel).where(EventModel.id == event_id).values(**update_event, available_seats=new_available_seats))
    await db.commit()
    await db.refresh(get_event)
    return get_event



@router.delete('/{event_id}', status_code=status.HTTP_200_OK, dependencies=[Depends(RoleCheck(correct_role=['admin']))])
async def delete_event(event_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]):

    get_event = await db.scalar(select(EventModel).where(
        EventModel.id == event_id,
        EventModel.is_active == True
    ))

    if get_event is None:
        raise HTTPException(
            status_code=404
        )
    
    check_booking_status = await db.scalar(select(BookingModel).where(
        BookingModel.event_id == event_id,
        BookingModel.status.in_(['pending', 'confirmed', 'checked_in'])
    ))
    if check_booking_status is not None:
        raise HTTPException(
            status_code=409
        )
    
    get_event.is_active = False
    await db.commit()
    return {'Message': 'Event has been delete'}



    