import time
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from .user import validate_credentials, get_user
from .. import models, schemas


def generate_token(db: Session, token: schemas.TokenCreate) -> models.Token:
    owner = get_user(db, token.owner_id)

    if not validate_credentials(owner, token.password):
        raise ValueError("invalid credentials")

    db_token = models.Token(
        value=str(uuid.uuid4()),
        owner_id=owner.id,
        lifetime=token.lifetime,
        creation_time=datetime.utcnow()
    )

    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return db_token


def find_token(db: Session, value: str) -> models.Token:
    token = db.get(models.Token, value)

    if token is None:
        raise LookupError(f"unknown token (value: {value})")

    return token


def expire_token(db: Session, token: models.Token):
    db.delete(token)
    db.commit()


def validate_token(db: Session, token: models.Token) -> models.User:
    if token.creation_time.timestamp() + token.lifetime < time.time():
        expire_token(db, token)
        raise ValueError("token has expired")

    user = db.get(models.User, token.owner_id)

    if user is None:
        raise LookupError("token is owned by an invalid user")

    return user
