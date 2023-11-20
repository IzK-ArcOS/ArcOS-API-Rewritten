from __future__ import annotations
from typing import Annotated

from fastapi import APIRouter, Depends, Body, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ._auth import get_user
from ._schemas import MessageCreate as cs_MessageCreate
from .._common import get_db
from ...davult.crud import message as message_db
from ...davult.models import User as m_User, Message as m_Message
from ...davult.schemas import MessageCreate as s_MessageCreate, Message as s_Message

router = APIRouter()


@router.get('/')
def get_all_messages(db: Annotated[Session, Depends(get_db)], user: Annotated[m_User, Depends(get_user)], count: int | None = None, offset: int = 0, descending: bool = True, preview_length: int | None = None, unread_only: bool = False) -> list[int] | list[s_Message]:
    return [s_Message(sender_id=message.sender_id, receiver_id=message.receiver_id, body=message.body[:preview_length], replying_id=message.replying_id, id=message.id, sent_time=message.sent_time, is_read=message.is_read, replier_ids=[message.id for message in message_db.get_replies(db, message)]) if preview_length is not None else message.id
            for message in sorted(filter(lambda m: not m.is_deleted and (not unread_only or not m.is_read), set(user.sent_messages + user.received_messages)), key=message_db.get_message_timestamp, reverse=descending)[offset:count and (count + offset)]]


@router.post('/')
def send_message(db: Annotated[Session, Depends(get_db)], user: Annotated[m_User, Depends(get_user)], message: Annotated[cs_MessageCreate, Body]) -> int:
    try:
        return message_db.send_message(db, s_MessageCreate(
            sender_id=user.id, receiver_id=message.recipient_id,
            body=message.body, replying_id=message.reply_id
        )).id
    except ValueError:
        raise HTTPException(status_code=413, detail="message is too big") from None


def _get_message(db: Annotated[Session, Depends(get_db)], user: Annotated[m_User, Depends(get_user)], message_id: int) -> m_Message:
    try:
        message = message_db.get_message(db, message_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="message is not found") from None
    else:
        if message not in user.sent_messages and message not in user.received_messages:
            raise HTTPException(status_code=403, detail="message was not sent to or sent by the user")
        else:
            return message


@router.get('/{message_id}')
def get_message(message: Annotated[m_Message, Depends(_get_message)]) -> s_Message:
    return s_Message(sender_id=message.sender_id, receiver_id=message.receiver_id, body=message.body, replying_id=message.replying_id, id=message.id, sent_time=message.sent_time, is_read=message.is_read)


@router.delete('/{message_id}')
def delete_message(db: Annotated[Session, Depends(get_db)], message: Annotated[m_Message, Depends(_get_message)]) -> None:
    message_db.delete_message(db, message)


class ThreadMessage(BaseModel):
    id: int
    repliers: list[ThreadMessage]


@router.get('/{message_id}/thread')
def get_message_thread(db: Annotated[Session, Depends(get_db)], message: Annotated[m_Message, Depends(_get_message)], user: Annotated[m_User, Depends(get_user)], depth: int | None = None, from_root: bool = False) -> ThreadMessage:
    def _get_thread_root(*, _message: m_Message = message) -> m_Message:
        nonlocal db

        if (reply_id := _message.replying_id) is not None:
            return _get_thread_root(_message=message_db.get_message(db, reply_id))
        else:
            return _message

    def _resolve_viewable_repliers(message: m_Message) -> list[m_Message]:
        nonlocal db

        return [reply for reply in message_db.get_replies(db, message) if reply in set(user.sent_messages + user.received_messages)]

    def _resolve_thread(message: m_Message, /, _depth: int | None = depth) -> ThreadMessage:
        nonlocal db

        if _depth is not None:
            _depth -= 1

        return ThreadMessage(id=message.id, repliers=[_resolve_thread(msg, _depth=_depth) for msg in _resolve_viewable_repliers(message)] if _depth is None or _depth > -1 else [])

    if depth < 0:
        raise HTTPException(status_code=422, detail="you cant go beyond the observable, into the unknown")

    if from_root:
        message = _get_thread_root()

    return _resolve_thread(message)
