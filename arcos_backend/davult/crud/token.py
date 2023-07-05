import time
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from .user import validate_credentials, get_user
from .. import models, schemas


def generate_token(db: Session, token: schemas.TokenCreate) -> models.Token:
    owner = get_user(db, token.owner_id)
    if not validate_credentials(db, owner.username, token.password):
        raise ValueError("invalid credentials")

    db.add(db_token := models.Token(
        value=str(uuid.uuid4()),
        owner_id=owner.id,
        lifetime=token.lifetime,
        creation_time=datetime.fromtimestamp(time.time())
    ))
    db.commit()
    db.refresh(db_token)

    time.sleep(0.25)

    return db_token


def find_token(db: Session, value: str) -> models.Token | None:
    return db.get(models.Token, value)


def expire_token(db: Session, token: models.Token):
    db.delete(token)
    db.commit()


def validate_token(db: Session, token: models.Token) -> models.User | None:
    if token.creation_time.timestamp() + token.lifetime < time.time():
        expire_token(db, token)
        return None

    return db.get(models.User, token.owner_id)
