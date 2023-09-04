import os

import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# FIXME resolve circular import some way or another
# from .._shared import configuration as cfg
with open("config.yaml") as f:
    cfg = yaml.safe_load(f)


SQLALCHEMY_DATABASE_URL = f"sqlite:///./{os.path.join(cfg['storage']['root'], cfg['storage']['database'])}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
LocalSession = sessionmaker(bind=engine)

Base = declarative_base()
