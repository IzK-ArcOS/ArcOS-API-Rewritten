from fastapi import APIRouter

from .session import router as session_api
from .users import router as users_api
from .messages import router as messages_api


router = APIRouter()

router.include_router(session_api, prefix='/token')
router.include_router(users_api, prefix='/users')
router.include_router(messages_api, prefix='/messages')
