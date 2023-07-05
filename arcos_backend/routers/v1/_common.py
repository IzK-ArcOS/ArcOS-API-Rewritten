import base64
from typing import Annotated

from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session

from ...davult import models
from ...davult.database import LocalSession
from ...davult.crud import token as token_db


def get_db() -> Session:
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


def auth_basic(authorization: Annotated[str, Header()]) -> tuple[str, str]:
    if not authorization.startswith('Basic '):
        raise HTTPException(status_code=422, detail="invalid authorization method")

    username, password = base64.b64decode(authorization[6:]).decode('utf-8').split(':')

    return username, password


def auth_bearer(db: Annotated[Session, Depends(get_db)], authorization: Annotated[str, Header()]) -> models.User:
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")

    token = token_db.find_token(db, authorization[7:])

    if token is None:
        raise HTTPException(status_code=403, detail="invalid token")

    try:
        user = token_db.validate_token(db, token)
    except ValueError or LookupError:
        raise HTTPException(status_code=403, detail="invalid token")

    return user


def get_path(path: str) -> str:
    return base64.b64decode(path).decode('utf-8')
