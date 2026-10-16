from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Role = Literal["manager", "waiter"]

class User(BaseModel):
    """Person who uses the application. Managers also administer the staff and see the reports."""

    id: int
    username: str
    full_name: str
    role: Role

class UserCreate(BaseModel):
    """JSON body to register a new member of staff."""

    model_config = ConfigDict(strict=True, extra="forbid", str_strip_whitespace=True)

    username: str = Field(min_length=3, max_length=30, pattern=r"^[a-z0-9._-]+$")
    full_name: str = Field(min_length=2, max_length=60)
    password: str = Field(min_length=6, max_length=128)
    role: Role = "waiter"

class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    username: str = Field(min_length=1, max_length=30)
    password: str = Field(min_length=1, max_length=128)

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
