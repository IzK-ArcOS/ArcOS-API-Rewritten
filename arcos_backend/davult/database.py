import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from .._shared import configuration as cfg


SQLALCHEMY_DATABASE_URL = f"sqlite:///./{os.path.join(cfg['storage']['root'], cfg['storage']['database'])}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
LocalSession = sessionmaker(bind=engine)

Base = declarative_base()
