from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..._utils import hash_salty, validate_username, dict2json, json2dict


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    if not validate_username(user.username):
        raise ValueError("invalid username")

    hashed_password = hash_salty(user.password)

    user = user.dict()

    del user['password']
    user['properties'] = dict2json(user['properties'])

    db_user = models.User(**user, hashed_password=hashed_password)

    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        raise RuntimeError("such username already exists")
    db.refresh(db_user)

    return db_user


def delete_user(db: Session, user: models.User):
    db.delete(user)


def get_user(db: Session, user_id: int) -> models.User:
    db_user = db.get(models.User, user_id)

    if db_user is None:
        raise LookupError(f"unknown user (ID: {user_id})")

    return db_user


def find_user(db: Session, username: str) -> models.User:
    db_user = db.query(models.User).filter(models.User.username == username).first()

    if db_user is None:
        raise LookupError(f"unknown user (username: {username})")

    return db_user


def rename_user(db: Session, user: models.User, new_name: str):
    if not validate_username(new_name):
        raise ValueError("invalid new name")

    user.username = new_name
    db.commit()


def set_user_password(db: Session, user: models.User, new_password: str):
    user.hashed_password = hash_salty(new_password)
    db.commit()


def update_user_properties(db: Session, user: models.User, properties: dict):
    updated_properties = json2dict(user.properties)
    updated_properties.update(properties)

    user.properties = dict2json(updated_properties)
    db.commit()


def get_users(db: Session) -> list[models.User]:
    return db.query(models.User).all()


def validate_credentials(db: Session, username: str, password: str) -> bool:
    return find_user(db, username).hashed_password == hash_salty(password)
