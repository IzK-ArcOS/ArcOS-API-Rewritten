import random
from datetime import datetime

from sqlalchemy.orm import Session

from .. import models, schemas


MAX_MESSAGE_LENGTH = 2000


def send_message(db: Session, message: schemas.MessageCreate) -> models.Message:
    if len(message.body) > MAX_MESSAGE_LENGTH:
        raise ValueError(f"too long message (>{MAX_MESSAGE_LENGTH})")

    db_message = models.Message(
        **message.dict(),
        id=random.randint(0, 999_999_999),
        sent_time=datetime.utcnow()
    )

    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return db_message


def delete_message(db: Session, message: models.Message):
    db.delete(message)


def get_message(db: Session, message_id: int) -> models.Message:
    message = db.get(models.Message, message_id)

    if message is None:
        raise LookupError(f"unknown message (ID: {message_id})")

    return message


def mark_read(db: Session, message: models.Message):
    if message.is_read:
        return

    message.is_read = True
    db.commit()


def get_replies(db: Session, message: models.Message) -> list[models.Message]:
    return db.query(models.Message).filter(models.Message.replying_id == message.id).all()
