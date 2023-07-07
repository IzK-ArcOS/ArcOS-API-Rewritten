from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ._common import get_db
from ..._utils import json2dict
from ...davult.crud import user as user_db


router = APIRouter()


@router.get('/get')
def users_get(db: Annotated[Session, Depends(get_db)]):
    users = user_db.get_users(db)

    return {
        'data': [{
            'username': user.username,
            'acc': json2dict(user.properties)['acc']
        } for user in users],
        'valid': True
    }
