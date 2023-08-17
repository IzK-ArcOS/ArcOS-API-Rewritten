import json
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ._common import get_db, auth_admin, user_identification
from ._schemas import UserEdit, UserData
from .. import EndpointTags
from ...davult import models
from ...davult.crud import user as user_db


router = APIRouter(tags=[EndpointTags.admin])


@router.delete('/user', summary="Deletes given user")
def admin_delete(_: Annotated[None, Depends(auth_admin)], db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(user_identification)]):
    user.user_delete(db, user)


@router.patch('/user', summary="Changes access properties of the given user")
def admin_change_user(_: Annotated[None, Depends(auth_admin)], db: Annotated[Session, Depends(get_db)], edit: UserEdit, user: Annotated[models.User, Depends(user_identification)]):
    if edit.password is not None:
        user_db.set_user_password(db, user, edit.password)

    if edit.state is not None:
        user_db.set_user_state(db, user, edit.state)


@router.get('/user', summary="Get user's data")
# FIXME read da fastapi docs - maybe there is a way to describe such situation
def admin_get_user(_: Annotated[None, Depends(auth_admin)], user: Annotated[models.User, Depends(user_identification)]) -> UserData:
    return UserData(
        id=user.id,
        username=user.username,
        properties=json.loads(user.properties),
        creation_time=user.creation_time,
        is_deleted=user.is_deleted,
    )
