from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.dataclasses import dataclass

from .models import USER_DEFAULT_PROPERTIES


MODEL_CONFIG = ConfigDict(from_attributes=True)


class TokenBase(BaseModel):
    owner_id: int
    lifetime: float


class TokenCreate(TokenBase):
    password: str


@dataclass(config=MODEL_CONFIG)
class Token(TokenBase):
    value: str
    creation_time: datetime


class UserBase(BaseModel):
    username: str
    properties: dict = USER_DEFAULT_PROPERTIES
    profile_picture: str | int = 3
    is_enabled: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    password: str


@dataclass(config=MODEL_CONFIG)
class User(UserBase):
    id: int
    tokens: list[Token] = []
