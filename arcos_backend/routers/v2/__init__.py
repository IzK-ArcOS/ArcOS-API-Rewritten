from fastapi import APIRouter
from .token import router as token_api
from .users import router as users_api
from .messages import router as messages_api
from .meta import router as meta_api

router = APIRouter()

router.include_router(token_api, prefix='/token')
router.include_router(users_api, prefix='/users')
router.include_router(messages_api, prefix='/messages')
router.include_router(meta_api, prefix='/meta')
