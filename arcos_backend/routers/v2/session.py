from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .._common import get_db
from ...davult.crud import token as token_db, user as user_db
from ...davult.models import Token
from ...davult.schemas import TokenCreate
from ._auth import OAuth2LoginInfo, get_token

router = APIRouter()


# TODO move it into
DEFAULT_TOKEN_LIFETIME = 60 * 60 * 24 * 7  # 1 week


# TODO scopes support
@router.post('/')
async def create_session(db: Annotated[Session, Depends(get_db)], login_info: Annotated[OAuth2PasswordRequestForm, Depends()]) -> OAuth2LoginInfo:
    try:
        user = user_db.find_user(db, login_info.username)
    except LookupError:
        # we do not do 401, as by using listing of all users it is possible to know if username or password is wrong
        raise HTTPException(status_code=404, detail="user not found") from None
    else:
        try:
            token = token_db.generate_token(db, TokenCreate(owner_id=user.id, lifetime=DEFAULT_TOKEN_LIFETIME, password=login_info.password))
        except ValueError:
            raise HTTPException(status_code=401, detail="password is invalid") from None
        else:
            return OAuth2LoginInfo(access_token=token.value)


@router.delete('/')
async def invalidate_session(db: Annotated[Session, Depends(get_db)], token: Annotated[Token, Depends(get_token)]) -> None:
    token_db.expire_token(db, token)
