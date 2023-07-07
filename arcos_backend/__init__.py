from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import _shared as shared; shared.init()  # NOQA E701
from ._shared import configuration as cfg
from .davult import models
from .davult.database import engine

from .filesystem import Filesystem
from .routers.v1 import server, token, user, users, filesystem, messages
from .authentication import AuthCodeMiddleware


def get_cfg():
    return cfg


models.Base.metadata.create_all(bind=engine)


app = FastAPI(title=cfg['info']['name'], version="always evolving :b")


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

app.include_router(server.router)
app.include_router(token.router)
app.include_router(user.router, prefix='/user')
app.include_router(users.router, prefix='/users')
app.include_router(filesystem.router, prefix='/fs')
app.include_router(messages.router, prefix='/messages')
