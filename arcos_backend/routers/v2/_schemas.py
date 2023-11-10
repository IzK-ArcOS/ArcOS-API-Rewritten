from pydantic import BaseModel


class PartialUserCredentials(BaseModel):
    username: str | None = None
    password: str | None = None
