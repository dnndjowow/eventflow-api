from pydantic import Field, BaseModel
from typing import Annotated

class AuthResponse(BaseModel):

    access_token: Annotated[str, Field()]
    refresh_token: Annotated[str, Field()]
    token_type: Annotated[str, Field()]


class AccessTokenResponse(BaseModel):

    access_token: Annotated[str, Field()]
    token_type: Annotated[str, Field()]


class RefreshTokenCreate(BaseModel):

    token: Annotated[str, Field()]