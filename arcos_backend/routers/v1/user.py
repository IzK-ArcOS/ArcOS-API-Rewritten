import base64
import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from ._common import auth_basic, auth_bearer
from .._common import get_db
from .. import EndpointTags
from ..._shared import filesystem as fs
from ..._utils import MAX_USERNAME_LEN
from ...davult import schemas, models
from ...davult.crud import user as user_db
from ...filesystem.userspace import Userspace


limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=[EndpointTags.users])


@router.get('/create', summary="Create new user")
@limiter.limit("7/hour")
def user_create(request: Request, db: Annotated[Session, Depends(get_db)], credentials: Annotated[tuple[str, str], Depends(auth_basic)]):
    username, password = credentials

    try:
        user = user_db.create_user(db, schemas.UserCreate(username=username, password=password))
    except ValueError:
        raise HTTPException(status_code=413, detail=f"username is too long (>{MAX_USERNAME_LEN})")
    except RuntimeError:
        raise HTTPException(status_code=409, detail="username already exists")

    Userspace(fs, user.id)

    return {'valid': True}


@router.get('/properties', summary="Get user properties")
def user_properties(user: Annotated[models.User, Depends(auth_bearer)]):
    return {**json.loads(user.properties), 'valid': True, 'statusCode': 200}


# not rate limited because frontend spams this endpoint as hell
@router.post('/properties/update', summary="Update user properties")
async def user_properties_update(request: Request, db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(auth_bearer)]):
    try:
        properties = json.JSONDecoder().decode((await request.body()).decode('utf-8'))
    except json.JSONDecodeError:
        raise HTTPException(status_code=422)

    user_db.update_user_properties(db, user, properties)


@router.get('/delete', summary="Delete the user")
# @limiter.limit("17/hour")   # XXX rate limiting disabled due to admin endpoint relying on this, and we dont want to rate limit admin endpoint
def user_delete(request: Request, db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(auth_bearer)]):
    userspace = Userspace(fs, user.id)
    user_db.delete_user(db, user)
    userspace.delete()


@router.get('/rename', summary="Change user's username")
def user_rename(db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(auth_bearer)], newname: str):
    newname = base64.b64decode(newname).decode('utf-8')
    try:
        user_db.rename_user(db, user, newname)
    except ValueError:
        raise HTTPException(status_code=413, detail=f"username is too long (>{MAX_USERNAME_LEN})")


@router.get('/changepswd', summary="Change user's password")
def user_changepswd(db: Annotated[Session, Depends(get_db)], credentials: Annotated[tuple[str, str], Depends(auth_basic)], new: str):
    new = base64.b64decode(new).decode('utf-8')
    username, password = credentials

    try:
        user = user_db.find_user(db, username)
    except LookupError:
        raise HTTPException(status_code=404)

    if not user_db.validate_credentials(user, password):
        raise HTTPException(status_code=403)

    user_db.set_user_password(db, user_db.find_user(db, username), new)
