import base64
from typing import Annotated

from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session

from .._common import get_db
from ..._shared import configuration as cfg
from ...davult import models
from ...davult.crud import token as token_db, user as user_db


def auth_basic(authorization: Annotated[str, Header()]) -> tuple[str, str]:
    if not authorization.startswith('Basic '):
        raise HTTPException(status_code=422, detail="invalid authorization method")

    username, password = base64.b64decode(authorization[6:]).decode('utf-8').split(':')

    return username.strip(), password


def auth_bearer(db: Annotated[Session, Depends(get_db)], authorization: Annotated[str, Header()]) -> models.User:
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")

    try:
        token = token_db.find_token(db, authorization[7:])
    except LookupError:
        raise HTTPException(status_code=403, detail="invalid token")

    if token is None:
        raise HTTPException(status_code=403, detail="invalid token")

    try:
        user = token_db.validate_token(db, token)
    except (ValueError, LookupError, RuntimeError):
        raise HTTPException(status_code=403, detail="invalid token")

    return user


def auth_bearer_param(db: Annotated[Session, Depends(get_db)], token: str) -> models.User:
    try:
        token = token_db.find_token(db, token)
    except LookupError:
        raise HTTPException(status_code=403, detail="invalid token")

    if token is None:
        raise HTTPException(status_code=403, detail="invalid token")

    try:
        user = token_db.validate_token(db, token)
    except (ValueError, LookupError):
        raise HTTPException(status_code=403, detail="invalid token")

    return user

def auth_admin(authorization: Annotated[str, Header()]):
    admin_code = cfg['security']['admin_code']

    if admin_code is None:
        raise HTTPException(status_code=403, detail="admin is disabled")

    if authorization != admin_code:
        raise HTTPException(status_code=403, detail="invalid code")


def get_path(path: str) -> str:
    return base64.b64decode(path).decode('utf-8')


def adapt_timestamp(timestamp: float) -> int:
    return round(timestamp * 1000)


def user_identification(db: Annotated[Session, Depends(get_db)], name: str | None = None, id: int | None = None) -> models.User:
    if not ((name is None) ^ (id is None)):
        raise HTTPException(status_code=422, detail="provide only either name or id")

    if name:
        return user_db.find_user(db, name)
    else:
        return user_db.get_user(db, id)
