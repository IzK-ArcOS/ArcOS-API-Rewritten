from typing import Final, Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .._common import get_db
from ...davult.models import Token, User
from ...davult.crud import token as token_db, user as user_db

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl='v2/token')


class OAuth2LoginInfo(BaseModel):
    access_token: str
    token_type: Final[str] = 'bearer'


async def get_token(db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(_oauth2_scheme)]) -> Token:
    try:
        return token_db.find_token(db, token)
    except LookupError:
        raise HTTPException(
            status_code=401,
            detail="invalid token",
            headers={'WWW-Authenticate': "Bearer"}
        ) from None


async def get_user(db: Annotated[Session, Depends(get_db)], token: Annotated[Token, Depends(get_token)]) -> User:
    try:
        return user_db.get_user(db, token.owner_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="associated user with the token was not found") from None
