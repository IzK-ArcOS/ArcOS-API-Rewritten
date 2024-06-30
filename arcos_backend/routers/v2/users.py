import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from ._auth import get_user
from ._schemas import PartialUserCredentials
from .._common import get_db, _verify_user_new_prop
from ..._shared import filesystem as fs
from ...davult.crud import user as user_db
from ...davult.models import User as m_User, is_enabled
from ...davult.schemas import User as s_User, UserBase as s_UserBase, UserCreate as s_UserCreate
from ...filesystem.userspace import Userspace

router = APIRouter()


@router.get('/')
def get_all_users(db: Annotated[Session, Depends(get_db)]) -> list[int]:
    return [user.id for user in user_db.get_users(db) if not user.is_deleted and is_enabled(user)]


@router.post('/')
def create_user(db: Annotated[Session, Depends(get_db)], user_data: s_UserCreate) -> int:
    try:
        return user_db.create_user(db, user_data).id
    except ValueError:
        raise HTTPException(status_code=422, detail="username is invalid") from None
    except RuntimeError:
        raise HTTPException(status_code=409, detail="username is occupied") from None


@router.get('/me')
def get_self(user: Annotated[m_User, Depends(get_user)]) -> s_User:
    return s_User(
        id=user.id,
        username=user.username,
        properties=json.loads(user.properties),
    )


@router.get('/{user_id}')
def get_foreign_user(db: Annotated[Session, Depends(get_db)], user_id: int) -> s_UserBase:
    try:
        user = user_db.get_user(db, user_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="user not found")
    else:
        return s_UserBase(username=user.username, properties={'acc': json.loads(user.properties)['acc']})


@router.delete('/me')
def delete_self(db: Annotated[Session, Depends(get_db)], user: Annotated[m_User, Depends(get_user)]) -> None:
    userspace = Userspace(fs, user.id)
    user_db.delete_user(db, user)
    userspace.delete()


@router.patch('/me')
def partial_edit_self(db: Annotated[Session, Depends(get_db)], user: Annotated[m_User, Depends(get_user)], data: Annotated[dict, Body]) -> None:
    _verify_user_new_prop(json.loads(user.properties), data)

    user_db.update_user_properties(db, user, data, replace=False)


@router.put('/me')
def full_edit_self(db: Annotated[Session, Depends(get_db)], user: Annotated[m_User, Depends(get_user)], data: Annotated[dict, Body]) -> None:
    _verify_user_new_prop(json.loads(user.properties), data)

    if (
            (acc := data.get('acc')) is None or
            not all(map(lambda k: k in acc, ('admin', 'enabled')))
    ):
        raise HTTPException(status_code=422)

    user_db.update_user_properties(db, user, data, replace=True)


@router.patch('/me/credentials')
def edit_credentials_self(db: Annotated[Session, Depends(get_db)], user: Annotated[m_User, Depends(get_user)], credentials: Annotated[PartialUserCredentials, Body]) -> None:
    if (username := credentials.username) is not None:
        user_db.rename_user(db, user, username)

    if (password := credentials.password) is not None:
        user_db.set_user_password(db, user, password)
