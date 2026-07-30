from pydantic import Field, field_validator, BaseModel, ConfigDict
from typing import Annotated


class UserCreate(BaseModel):
    username: Annotated[str, Field(...,min_length=3, max_length=50)]
    password: Annotated[str, Field(..., min_length=5, max_length=30)]
    
    @field_validator('username', mode='after')
    @classmethod
    def check_username(cls, value: str):
        
        if len(value.strip()) == 0:
            raise ValueError()
        
        if any(role in value.strip().lower() for role in ['admin', 'manager', 'customer']):
            raise ValueError()
        
        return value


class UserResponse(BaseModel):
    id: Annotated[int, Field()]
    username: Annotated[str, Field()]
    role: Annotated[str, Field()]
    is_active: Annotated[bool, Field()]

    model_config = ConfigDict(from_attributes=True)
