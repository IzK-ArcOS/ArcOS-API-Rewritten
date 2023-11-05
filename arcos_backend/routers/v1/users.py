import json
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ._common import get_db
from .. import EndpointTags
from ...davult.models import is_enabled
from ...davult.crud import user as user_db

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=[EndpointTags.users])


@router.get('/get', summary="Get the list of users")
@limiter.limit("1/second")
def users_get(request: Request, db: Annotated[Session, Depends(get_db)]):
    users = user_db.get_users(db)

    return {
        'data': sorted([{
            'username': user.username,
            'acc': json.loads(user.properties)['acc']
        } for user in users if not user.is_deleted and is_enabled(user)], key=lambda item: item['username']),
        'valid': True
    }
