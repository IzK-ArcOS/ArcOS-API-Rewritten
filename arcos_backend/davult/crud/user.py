import json
import random
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import message as msg_db, token as token_db
from .. import models, schemas
from ..._utils import hash_salty, validate_username, check_profanity, MAX_USERNAME_LEN


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    if not validate_username(user.username):
        raise ValueError(f"username is too long (>{MAX_USERNAME_LEN})")

    if check_profanity(user.username):
        raise ValueError(f"username contains offensive strings")

    hashed_password = hash_salty(user.password)

    user = user.dict()

    del user['password']
    user['properties'] = json.dumps(user['properties'])

    db_user = models.User(
        **user,
        id=random.randint(0, 999_999_999),
        hashed_password=hashed_password,
        creation_time=datetime.utcnow()
    )

    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        raise RuntimeError("such username already exists")
    db.refresh(db_user)

    return db_user


def delete_user(db: Session, user: models.User):
    user.username = f'deleted#{user.id}'
    user.properties = "{}"
    user.hashed_password = None
    user.is_deleted = True
    db.commit()

    for message in user.sent_messages:
        msg_db.delete_message(db, message)

    for token in user.tokens:
        token_db.expire_token(db, token)


def get_user(db: Session, user_id: int) -> models.User:
    db_user = db.get(models.User, user_id)

    if db_user is None:
        raise LookupError(f"unknown user (ID: {user_id})")

    return db_user


def find_user(db: Session, username: str) -> models.User:
    db_user = db.query(models.User).filter(
        models.User.username == username).first()

    if db_user is None:
        raise LookupError(f"unknown user (username: {username})")

    return db_user


def rename_user(db: Session, user: models.User, new_username: str):
    if not validate_username(new_username):
        raise ValueError(f"new username is too long (>{MAX_USERNAME_LEN})")

    user.username = new_username
    db.commit()


def set_user_password(db: Session, user: models.User, new_password: str):
    user.hashed_password = hash_salty(new_password)
    db.commit()


def set_user_state(db: Session, user: models.User, state: bool):
    properties = json.loads(user.properties)
    properties['acc']['enabled'] = state
    user.properties = json.dumps(properties)
    db.commit()

    # if banning -> invalidate all tokens
    if not state:
        for token in user.tokens:
            token_db.expire_token(db, token)


def update_user_properties(db: Session, user: models.User, properties: dict):
    updated_properties = json.loads(user.properties)
    updated_properties.update(properties)
    user.properties = json.dumps(updated_properties)
    db.commit()


def get_users(db: Session) -> list[models.User]:
    return db.query(models.User).all()


def validate_credentials(user: models.User, password: str) -> bool:
    return user.hashed_password == hash_salty(password)
