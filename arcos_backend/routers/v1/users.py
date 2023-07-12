from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ._common import get_db
from .. import EndpointTags
from ..._utils import json2dict
from ...davult.models import is_enabled
from ...davult.crud import user as user_db


router = APIRouter(tags=[EndpointTags.users])


@router.get('/get', summary="Get the list of users")
def users_get(db: Annotated[Session, Depends(get_db)]):
    users = user_db.get_users(db)

    return {
        'data': [{
            'username': user.username,
            'acc': json2dict(user.properties)['acc']
        } for user in users if not user.is_deleted and is_enabled(user)],
        'valid': True
    }
