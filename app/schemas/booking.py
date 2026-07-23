from pydantic import Field, field_validator, ConfigDict, BaseModel
from typing import Annotated
from datetime import datetime
from decimal import Decimal



class BookingCreate(BaseModel):
    event_id: Annotated[int, Field(...)]
    seats: Annotated[int, Field(..., ge=1, le=10)]


class BookingStatusPatch(BaseModel):
    status: Annotated[str, Field(...)]

    @field_validator('status', mode='after')
    @classmethod
    def check_status(cls, value: str):
        if value not in ['pending', 'confirmed', 'checked_in', 'completed', 'cancelled']:
            raise ValueError()
        return value
    
    
class BookingResponse(BaseModel):
    id: Annotated[int, Field()]
    user_id: Annotated[int, Field()]
    event_id: Annotated[int, Field()]
    seats: Annotated[int, Field()]
    unit_price: Annotated[Decimal, Field()]
    total_amount: Annotated[Decimal, Field()]
    status: Annotated[str, Field()]
    created_at: Annotated[datetime, Field()]
    updated_at: Annotated[datetime | None, Field()]

    model_config = ConfigDict(from_attributes=True)