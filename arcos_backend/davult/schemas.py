from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.dataclasses import dataclass

from .models import USER_DEFAULT_PROPERTIES


# TODO make it default
# MODEL_CONFIG = ConfigDict(from_attributes=True)


# TODO remake without usage of inheritance


class UserBase(BaseModel):
    username: str
    properties: dict = USER_DEFAULT_PROPERTIES


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int


class TokenBase(BaseModel):
    owner_id: int
    lifetime: float


class TokenCreate(TokenBase):
    password: str


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


class Message(MessageBase):
    id: int
    sent_time: datetime
    is_read: bool
    replier_ids: list[int]
