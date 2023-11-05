from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from . import _shared as shared; shared.init()  # NOQA E701
from ._shared import configuration as cfg
from .davult import models
from .davult.database import engine

from .filesystem import Filesystem
from .routers import TAGS_DOCS
from .routers.v1 import meta, token, user, users, filesystem, messages, admin
from .authentication import AuthCodeMiddleware
from ._logging import LoggingMiddleware


def get_cfg():
    return cfg


models.Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title=cfg['info']['name'],
    version="always evolving :b",
    openapi_tags=TAGS_DOCS
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# tells cors to fuck off
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(
    AuthCodeMiddleware,
    authcode=cfg['security']['auth_code']
)

app.add_middleware(
    LoggingMiddleware
)


app.include_router(meta.router)
app.include_router(token.router)
app.include_router(user.router, prefix='/user')
app.include_router(users.router, prefix='/users')
app.include_router(filesystem.router, prefix='/fs')
app.include_router(messages.router, prefix='/messages')
app.include_router(admin.router, prefix='/admin')
