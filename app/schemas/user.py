from pydantic import Field, field_validator, BaseModel, ConfigDict
from typing import Annotated


class UserCreate(BaseModel):
    username: Annotated[str, Field(...,min_length=3 ,max_length=50)]
    token: Annotated[str, Field(...,min_length=3 ,max_length=100)]
    role: Annotated[str, Field(...)]

    @field_validator('role', mode='after')
    @classmethod
    def check_role(cls, value: str):
        if value not in ['admin', 'manager', 'customer']:
            raise ValueError()
        return value


class UserResponse(BaseModel):
    id: Annotated[int, Field()]
    username: Annotated[str, Field()]
    role: Annotated[str, Field()]
    is_active: Annotated[bool, Field()]

    model_config = ConfigDict(from_attributes=True)
