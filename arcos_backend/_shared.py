import os
import shutil

import yaml

from .database import Database
from .filesystem import Filesystem


API_REVISION = 1


configuration: dict
database: Database
filesystem: Filesystem

_is_initialized: bool = False


def init():
    global configuration, database, filesystem, _is_initialized

    if _is_initialized:
        raise RuntimeError("shared variables are already initialized")
    else:
        _is_initialized = True

    # load config file, create it if not found
    if not os.path.isfile("config.yaml"):
        shutil.copy(os.path.join("arcos_backend", "assets", "default", "config.default.yaml"), "config.yaml")
    with open("config.yaml") as f:
        configuration = yaml.safe_load(f)

    storage_cfg = configuration['storage']
    os.makedirs(storage_cfg['root'], exist_ok=True)

    database = Database(os.path.join(storage_cfg['root'], storage_cfg['database']))

    filesystem = Filesystem(os.path.join(storage_cfg['root'], storage_cfg['filesystem']),
                            os.path.join(storage_cfg['root'], storage_cfg['template']) if storage_cfg['template'] is not None else None,
                            configuration['filesystem']['userspace_size'])
