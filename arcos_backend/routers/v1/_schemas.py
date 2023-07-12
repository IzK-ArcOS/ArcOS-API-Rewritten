from pydantic import BaseModel


class UserEdit(BaseModel):
    password: str | None = None
    state: bool | None = None
