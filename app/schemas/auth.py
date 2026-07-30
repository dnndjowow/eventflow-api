from pydantic import Field, BaseModel
from typing import Annotated

class AuthResponse(BaseModel):

    access_token: Annotated[str, Field()]
    token_type: Annotated[str, Field()]