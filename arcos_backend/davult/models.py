import json
import os

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base
from .._utils import dict2json


with open(os.path.join("arcos_backend", "assets", "default", "properties.default.json")) as f:
    USER_DEFAULT_PROPERTIES = json.load(f)
    USER_DEFAULT_PROPERTIES_STR = dict2json(USER_DEFAULT_PROPERTIES)


class Token(Base):
    __tablename__ = "tokens"

    value = Column(String, primary_key=True, index=True)
    owner_id = Column(ForeignKey("users.id"))
    lifetime = Column(Float)
    creation_time = Column(DateTime)

    owner = relationship("User", back_populates="tokens")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(ForeignKey("users.id"))
    receiver_id = Column(ForeignKey("users.id"))
    body = Column(String)
    replying_id = Column(ForeignKey("messages.id"), default=None)
    sent_time = Column(DateTime)
    is_read = Column(Boolean, default=False)

    sender = relationship("User", back_populates="sent_messages", foreign_keys=sender_id)
    receiver = relationship("User", back_populates="received_messages", foreign_keys=receiver_id)
    # replies = relationship("Message", back_populates="replies", remote_side=[id])  # TODO make da thing to work


class User(Base):
    global USER_DEFAULT_PROPERTIES

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    properties = Column(String, default=USER_DEFAULT_PROPERTIES_STR)

    tokens = relationship("Token", back_populates="owner")
    sent_messages = relationship("Message", back_populates="sender", foreign_keys=Message.sender_id)
    received_messages = relationship("Message", back_populates="receiver", foreign_keys=Message.receiver_id)
