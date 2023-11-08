from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address


from ._common import auth_basic, get_db
from .. import EndpointTags
from ..._shared import configuration as cfg
from ...davult import schemas
from ...davult.models import is_enabled
from ...davult.crud import token as token_db, user as user_db


limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=[EndpointTags.sessions])


@router.get('/auth', summary="Create session")
@limiter.limit("15/minute")
def auth(request: Request, db: Annotated[Session, Depends(get_db)], credentials: Annotated[tuple[str, str], Depends(auth_basic)]):
    username, password = credentials

    try:
        user = user_db.find_user(db, username)
    except LookupError:
        raise HTTPException(status_code=404, detail="user not found")

    if not is_enabled(user):
        raise HTTPException(status_code=403, detail="user is disabled")

    try:
        token = token_db.generate_token(db, schemas.TokenCreate(
            owner_id=user.id,
            password=password,
            lifetime=cfg['security']['token_lifetime']
        ))
    except ValueError:
        raise HTTPException(status_code=403, detail="invalid credentials")

    return {'data': {'username': user.username, 'token': token.value}, 'valid': True, "error": {"title": "", "message": ""}}


@router.get('/logoff', summary="Expire session")
@limiter.limit("15/minute")
def logoff(request: Request, db: Annotated[Session, Depends(get_db)], authorization: Annotated[str, Header()]):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")

    try:
        token_db.expire_token(db, token_db.find_token(db, authorization[7:]))
    except LookupError:
        raise HTTPException(status_code=404, detail="token not found")
