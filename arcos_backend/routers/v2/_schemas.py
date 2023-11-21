from pydantic import BaseModel


class PartialUserCredentials(BaseModel):
    username: str | None = None
    password: str | None = None


class MessageCreate(BaseModel):
    recipient_id: int
    body: str
    reply_id: int | None = None


class MetaInfo(BaseModel):
    protected: bool
    revision: int
    name: str
