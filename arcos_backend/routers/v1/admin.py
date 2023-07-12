from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from . import user
from ._common import get_db, auth_admin
from ._schemas import UserEdit
from .. import EndpointTags
from ...davult.crud import user as user_db


router = APIRouter(tags=[EndpointTags.admin])


@router.delete('/user', summary="Deletes given user")
def admin_delete(_: Annotated[None, Depends(auth_admin)], db: Annotated[Session, Depends(get_db)], name: str):
    user.user_delete(db, user_db.find_user(db, name))


@router.put('/user', summary="Changes access properties of the given user")
def admin_change_user(_: Annotated[None, Depends(auth_admin)], db: Annotated[Session, Depends(get_db)], edit: UserEdit, name: str):
    user = user_db.find_user(db, name)

    if edit.password is not None:
        user_db.set_user_password(db, user, edit.password)

    if edit.state is not None:
        user_db.set_user_state(db, user, edit.state)
