from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import user
from ._common import get_db, auth_admin
from ._schemas import UserEdit, UserData
from .. import EndpointTags
from ...davult.crud import user as user_db


router = APIRouter(tags=[EndpointTags.admin])


@router.delete('/user', summary="Deletes given user")
def admin_delete(_: Annotated[None, Depends(auth_admin)], db: Annotated[Session, Depends(get_db)], name: str):
    user.user_delete(db, user_db.find_user(db, name))


@router.patch('/user', summary="Changes access properties of the given user")
def admin_change_user(_: Annotated[None, Depends(auth_admin)], db: Annotated[Session, Depends(get_db)], edit: UserEdit, name: str):
    user = user_db.find_user(db, name)

    if edit.password is not None:
        user_db.set_user_password(db, user, edit.password)

    if edit.state is not None:
        user_db.set_user_state(db, user, edit.state)


@router.get('/user', summary="Get user's data")
# FIXME read da fastapi docs - maybe there is a way to describe such situation
def admin_get_user(_: Annotated[None, Depends(auth_admin)], db: Annotated[Session, Depends(get_db)], name: str | None = None, id: int | None = None):
    if not (bool(name) ^ bool(id)):
        raise HTTPException(status_code=422, detail="provide only either name or id")

    if name:
        user = user_db.find_user(db, name)
    else:
        user = user_db.get_user(db, id)

    return {
        'id': user.id,
        'username': user.username,
        'properties': user.properties,
        'creation_time': user.creation_time,
        'is_deleted': user.is_deleted
    }
