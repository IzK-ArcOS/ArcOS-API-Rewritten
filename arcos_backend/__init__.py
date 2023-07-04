import os.path
import shutil

import yaml
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from . import database, filesystem
from .api import v1
from . import _shared as shared


# load config file, create it if not found
if not os.path.isfile("config.yaml"):
    shutil.copy(os.path.join("arcos_backend", "assets", "config.default.yaml"), "config.yaml")
with open("config.yaml") as f:
    shared.configuration = yaml.safe_load(f)

shared.database = database.Database(os.path.join("data", "arcos.sqlite"))
shared.filesystem = filesystem.Filesystem(os.path.join("data", "filesystem"),
                                          os.path.join("data", "template"),
                                          shared.configuration['filesystem']['userspace_size'])

app = FastAPI(title=shared.configuration['name'], version="0.0.1")

# tells cors to fuck off
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(v1.router)
