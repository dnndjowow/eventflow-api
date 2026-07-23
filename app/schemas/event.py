from pydantic import Field, field_validator, ConfigDict, BaseModel, model_validator
from typing import Annotated
from datetime import datetime

from decimal import Decimal



class EventCreate(BaseModel):
    title: Annotated[str, Field(..., max_length=120)]
    capacity: Annotated[int, Field(..., ge=1)]
    price: Annotated[Decimal, Field(..., ge=0, max_digits=10, decimal_places=2)]
    booking_deadline: Annotated[datetime, Field(...)]
    starts_at: Annotated[datetime, Field(...)]

    @field_validator('title', mode='after')
    @classmethod
    def check_title(cls, value: str):
        if value.strip().lower() in ['test', 'empty', 'admin']:
            raise ValueError()
        return value
    
    @field_validator('booking_deadline', mode='after')
    @classmethod
    def check_booking_deadline_for_now(cls, value: datetime):
        if value < datetime.now():
            raise ValueError()
        return value
    

    @model_validator(mode='after')
    def check_booking_deadline(self):
        if self.booking_deadline >= self.starts_at:
            raise ValueError()
        return self
    

    @field_validator('starts_at', mode='after')
    @classmethod
    def check_starts_at(cls, value: datetime):
        if value < datetime.now():
            raise ValueError
        return value
    

class EventPatch(BaseModel):
    title: Annotated[str | None, Field(max_length=120)] = None
    capacity: Annotated[int | None, Field(ge=1)] = None
    price: Annotated[Decimal | None, Field(ge=0, max_digits=10, decimal_places=2)] = None
    booking_deadline: Annotated[datetime | None, Field()] = None
    starts_at: Annotated[datetime | None, Field()] = None

    @field_validator('title', mode='after')
    @classmethod
    def check_title(cls, value: str | None):
        if value is None:
            raise ValueError()
        
        if value.strip().lower() in ['test', 'empty', 'admin']:
            raise ValueError()
        return value
    

    @model_validator(mode='after')
    def check_booking_deadline(self):
        if self.booking_deadline is not None and self.starts_at is not None:
            if self.booking_deadline >= self.starts_at:
                raise ValueError()
            return self
        return self
        
        
    @field_validator(
        "title",
        "capacity",
        "price",
        "booking_deadline",
        "starts_at",
        mode="after",
    )
    @classmethod
    def check_for_none(cls, value):
        if value is None:
            raise ValueError()
        return value
    

    @field_validator('booking_deadline', mode='after')
    @classmethod
    def check_booking_deadline_for_none(cls, value: datetime | None):
        if value is None:
            raise ValueError()
        
        if value < datetime.now():
            raise ValueError()
        return value

    @field_validator('starts_at', mode='after')
    @classmethod
    def check_starts_at(cls, value: datetime | None):
        if value is None:
            raise ValueError()
        
        if value < datetime.now():
            raise ValueError
        return value


class EventResponse(BaseModel):
    id: Annotated[int, Field()]
    title: Annotated[str, Field()]
    capacity: Annotated[int, Field()]
    available_seats: Annotated[int, Field()]
    price: Annotated[Decimal, Field()]
    booking_deadline: Annotated[datetime, Field()]
    starts_at: Annotated[datetime, Field()]
    is_active: Annotated[bool, Field()]
    created_at: Annotated[datetime, Field()]

    model_config = ConfigDict(from_attributes=True)