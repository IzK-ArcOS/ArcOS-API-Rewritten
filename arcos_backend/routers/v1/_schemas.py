from datetime import datetime

from pydantic import BaseModel


class UserEdit(BaseModel):
    password: str | None = None
    state: bool | None = None


class UserData(BaseModel):
    id: int
    username: str
    properties: dict
    creation_time: datetime
    is_deleted: bool
