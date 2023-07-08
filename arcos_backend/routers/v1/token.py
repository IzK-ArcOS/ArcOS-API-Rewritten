from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Depends

from ._common import auth_basic, get_token_db, get_user_db
from ..._shared import configuration as cfg
from ...davult import schemas
from ...davult.crud.token import TokenDB
from ...davult.crud.user import UserDB


router = APIRouter()


@router.get('/auth')
def auth(user_db: Annotated[UserDB, Depends(get_user_db)], token_db: Annotated[TokenDB, Depends(get_token_db)], credentials: Annotated[tuple[str, str], Depends(auth_basic)]):
    username, password = credentials

    try:
        user = user_db.find_user(username)
    except LookupError:
        raise HTTPException(status_code=404, detail="user not found")

    try:
        token = token_db.generate_token(schemas.TokenCreate(
            owner_id=user.id,
            password=password,
            lifetime=cfg['security']['token_lifetime']
        ))
    except ValueError:
        raise HTTPException(status_code=403, detail="invalid credentials")

    return {'data': {'username': user.username, 'token': token.value}, 'valid': True, "error": {"title": "", "message": ""}}


@router.get('/logoff')
def logoff(token_db: Annotated[TokenDB, Depends(get_token_db)], authorization: Annotated[str, Header()]):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")

    try:
        token_db.expire_token(token_db.find_token(authorization[7:]))
    except LookupError:
        raise HTTPException(status_code=404, detail="token not found")
