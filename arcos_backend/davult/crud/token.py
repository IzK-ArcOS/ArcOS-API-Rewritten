import time
import uuid
from datetime import datetime

from . import CRUD, user
from .. import models, schemas


class TokenDB(CRUD):

    def generate_token(self, token: schemas.TokenCreate) -> models.Token:
        user_db = user.UserDB()

        owner = user_db.get_user(token.owner_id)

        if not user_db.validate_credentials(owner, token.password):
            raise ValueError("invalid credentials")

        db_token = models.Token(
            value=str(uuid.uuid4()),
            owner_id=owner.id,
            lifetime=token.lifetime,
            creation_time=datetime.utcnow()
        )

        self._db.add(db_token)
        self._db.commit()
        self._db.refresh(db_token)

        return db_token

    def find_token(self, value: str) -> models.Token:
        token = self._db.get(models.Token, value)

        if token is None:
            raise LookupError(f"unknown token (value: {value})")

        return token

    def expire_token(self, token: models.Token):
        self._db.delete(token)
        self._db.commit()

    def validate_token(self, token: models.Token) -> models.User:
        if token.creation_time.timestamp() + token.lifetime < time.time():
            self.expire_token(token)
            raise ValueError("token has expired")

        user = self._db.get(models.User, token.owner_id)

        if user is None:
            raise LookupError("token is owned by an invalid user")

        return user
