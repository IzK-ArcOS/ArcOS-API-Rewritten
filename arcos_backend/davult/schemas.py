from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.dataclasses import dataclass

from .models import USER_DEFAULT_PROPERTIES


MODEL_CONFIG = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    username: str
    properties: dict = USER_DEFAULT_PROPERTIES


class UserCreate(UserBase):
    password: str


@dataclass(config=MODEL_CONFIG)
class User(UserBase):
    id: int


class TokenBase(BaseModel):
    owner_id: int
    lifetime: float


class TokenCreate(TokenBase):
    password: str


@dataclass(config=MODEL_CONFIG)
class Token(TokenBase):
    value: str
    creation_time: datetime


class MessageBase(BaseModel):
    sender_id: int
    receiver_id: int
    body: str
    replying_id: int | None = None


class MessageCreate(MessageBase):
    pass


@dataclass(config=MODEL_CONFIG)
class Message(MessageBase):
    id: int
    sent_time: datetime
    is_read: bool
