from typing import Annotated

from fastapi import APIRouter, Header, HTTPException

from ._auth import basic
from ..._shared import database as db, configuration as cfg


router = APIRouter()


@router.get('/auth')
def auth(authorization: Annotated[str, Header()]):
    username, password = basic(authorization)

    token = db.generate_token(username, password, cfg['security']['token_lifetime'])

    return {'data': {'username': username, 'token': token}, 'valid': True, "error": {"title": "", "message": ""}}


@router.get('/logoff')
def logoff(authorization: Annotated[str, Header()]):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")
    token = authorization[7:]

    db.expire_token(token)
