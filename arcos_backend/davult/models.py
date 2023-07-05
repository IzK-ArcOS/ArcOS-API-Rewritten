import json
import os

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base
from .._utils import dict2json


with open(os.path.join("arcos_backend", "assets", "default", "properties.default.json")) as f:
    USER_DEFAULT_PROPERTIES = json.load(f)
    USER_DEFAULT_PROPERTIES_STR = dict2json(USER_DEFAULT_PROPERTIES)


class User(Base):
    global USER_DEFAULT_PROPERTIES

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    properties = Column(String, default=USER_DEFAULT_PROPERTIES_STR)
    # profile_picture = Column(String, default="3")
    # is_enabled = Column(Boolean, default=True)
    # is_admin = Column(Boolean, default=False)

    tokens = relationship("Token", back_populates="owner")


class Token(Base):
    __tablename__ = "tokens"

    value = Column(String, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    lifetime = Column(Float)
    creation_time = Column(DateTime)

    owner = relationship("User", back_populates="tokens")
