import random
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from . import CRUD, token as tkn_db, message as message_db
from .. import models, schemas
from ..._utils import hash_salty, validate_username, dict2json, json2dict, MAX_USERNAME_LEN


class UserDB(CRUD):
    def create_user(self,  user: schemas.UserCreate) -> models.User:
        if not validate_username(user.username):
            raise ValueError(f"username is too long (>{MAX_USERNAME_LEN})")

        hashed_password = hash_salty(user.password)

        user = user.dict()

        del user['password']
        user['properties'] = dict2json(user['properties'])

        db_user = models.User(
            **user,
            id=random.randint(0, 999_999_999),
            hashed_password=hashed_password,
            creation_time=datetime.utcnow()
        )

        self._db.add(db_user)
        try:
            self._db.commit()
        except IntegrityError:
            raise RuntimeError("such username already exists")
        self._db.refresh(db_user)

        return db_user

    def delete_user(self,  user: models.User):
        user.username = f'deleted#{user.id}'
        user.properties = None
        user.hashed_password = None

        msg_db = message_db.MessageDB()
        for message in user.sent_messages:
            msg_db.delete_message(message)

        token_db = tkn_db.TokenDB()
        for token in user.tokens:
            token_db.expire_token(token)

        user.is_deleted = True
        self._db.commit()

    def get_user(self,  user_id: int) -> models.User:
        db_user = self._db.get(models.User, user_id)

        if db_user is None:
            raise LookupError(f"unknown user (ID: {user_id})")

        return db_user

    def find_user(self,  username: str) -> models.User:
        db_user = self._db.query(models.User).filter(models.User.username == username).first()

        if db_user is None:
            raise LookupError(f"unknown user (username: {username})")

        return db_user

    def rename_user(self,  user: models.User, new_username: str):
        if not validate_username(new_username):
            raise ValueError(f"new username is too long (>{MAX_USERNAME_LEN})")

        user.username = new_username
        self._db.commit()

    def set_user_password(self,  user: models.User, new_password: str):
        user.hashed_password = hash_salty(new_password)
        self._db.commit()

    def update_user_properties(self,  user: models.User, properties: dict):
        updated_properties = json2dict(user.properties)
        updated_properties.update(properties)

        user.properties = dict2json(updated_properties)
        self._db.commit()

    def get_users(self) -> list[models.User]:
        return self._db.query(models.User).all()

    @staticmethod
    def validate_credentials(user: models.User, password: str) -> bool:
        return user.hashed_password == hash_salty(password)
