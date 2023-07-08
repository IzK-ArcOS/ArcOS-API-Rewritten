import random
from datetime import datetime

from . import CRUD
from .. import models, schemas


MAX_MESSAGE_LENGTH = 2000


class MessageDB(CRUD):
    def send_message(self, message: schemas.MessageCreate) -> models.Message:
        if len(message.body) > MAX_MESSAGE_LENGTH:
            raise ValueError(f"too long message (>{MAX_MESSAGE_LENGTH})")

        db_message = models.Message(
            **message.dict(),
            id=random.randint(0, 999_999_999),
            sent_time=datetime.utcnow()
        )

        self._db.add(db_message)
        self._db.commit()
        self._db.refresh(db_message)

        return db_message

    def delete_message(self, message: models.Message):
        message.body = "[ deleted ]"
        message.is_deleted = True
        self._db.commit()

    def get_message(self, message_id: int) -> models.Message:
        message = self._db.get(models.Message, message_id)

        if message is None:
            raise LookupError(f"unknown message (ID: {message_id})")

        return message

    def mark_read(self, message: models.Message):
        if message.is_read:
            return

        message.is_read = True
        self._db.commit()

    def get_replies(self, message: models.Message) -> list[models.Message]:
        return self._db.query(models.Message).filter(models.Message.replying_id == message.id).all()
