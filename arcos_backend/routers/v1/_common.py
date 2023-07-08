import base64
from typing import Annotated

from fastapi import HTTPException, Header, Depends

from ...davult import models
from ...davult.crud.message import MessageDB
from ...davult.crud.token import TokenDB
from ...davult.crud.user import UserDB


def get_user_db() -> UserDB:
    return UserDB()


def get_token_db() -> TokenDB:
    return TokenDB()


def get_msg_db() -> MessageDB:
    return MessageDB()


def auth_basic(authorization: Annotated[str, Header()]) -> tuple[str, str]:
    if not authorization.startswith('Basic '):
        raise HTTPException(status_code=422, detail="invalid authorization method")

    username, password = base64.b64decode(authorization[6:]).decode('utf-8').split(':')

    return username, password


def auth_bearer(token_db: Annotated[TokenDB, Depends(get_token_db)], authorization: Annotated[str, Header()]) -> models.User:
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")

    try:
        token = token_db.find_token(authorization[7:])
    except LookupError:
        raise HTTPException(status_code=403, detail="invalid token")

    if token is None:
        raise HTTPException(status_code=403, detail="invalid token")

    try:
        user = token_db.validate_token(token)
    except (ValueError, LookupError):
        raise HTTPException(status_code=403, detail="invalid token")

    return user


def get_path(path: str) -> str:
    return base64.b64decode(path).decode('utf-8')


def adapt_timestamp(timestamp: float) -> int:
    return round(timestamp * 1000)
