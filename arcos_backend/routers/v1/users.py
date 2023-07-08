from typing import Annotated

from fastapi import APIRouter, Depends

from ._common import get_user_db
from ..._utils import json2dict
from ...davult.crud.user import UserDB


router = APIRouter()


@router.get('/get')
def users_get(user_db: Annotated[UserDB, Depends(get_user_db)]):
    return {
        'data': [{
            'username': user.username,
            'acc': json2dict(user.properties)['acc']
        } for user in user_db.get_users() if not user.is_deleted],
        'valid': True
    }
