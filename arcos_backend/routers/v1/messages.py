import base64
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from starlette.requests import Request

from ._common import get_db, auth_bearer, adapt_timestamp
from .. import EndpointTags
from ...davult import models, schemas
from ...davult.crud import message as msg_db, user as user_db

MESSAGE_PREVIEW_BODY_LEN = 30


limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=[EndpointTags.messages])


def get_id(id: str) -> int:
    try:
        return int(base64.b64decode(id).decode('utf-8'))
    except ValueError:
        raise HTTPException(status_code=422, detail="your id is invalid")


def get_target(db: Annotated[Session, Depends(get_db)], target: str) -> models.User:
    return user_db.find_user(db, base64.b64decode(target).decode('utf-8'))


@router.post('/send', summary="Send the message")
@limiter.limit("1/second")
async def messages_send(request: Request, db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(auth_bearer)], target: Annotated[models.User, Depends(get_target)]):
    try:
        message = msg_db.send_message(db, schemas.MessageCreate(
            sender_id=user.id,
            receiver_id=target.id,
            body=(await request.body()).decode('utf-8')
        ))
    except ValueError:
        raise HTTPException(status_code=413)

    return {
        'valid': True,
        'data': {
            'sender': user.username,
            'receiver': target.username,
            'id': message.id
        }
    }


@router.post('/reply', summary="Reply to the message")
@limiter.limit("1/second")
async def messages_reply(request: Request, db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(auth_bearer)], id: int, target: Annotated[models.User, Depends(get_target)]):
    try:
        message = msg_db.send_message(db, schemas.MessageCreate(
            sender_id=user.id,
            receiver_id=target.id,
            body=(await request.body()).decode('utf-8'),
            replying_id=id
        ))
    except ValueError:
        raise HTTPException(status_code=413)

    return {
        'valid': True,
        'data': {
            'sender': user.username,
            'receiver': target.username,
            'id': message.id,
            'replier': id
        }
    }


@router.get('/get', summary="Get contents of the message")
def messages_get(db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(auth_bearer)], id: Annotated[int, Depends(get_id)]):
    try:
        message = msg_db.get_message(db, id)
    except LookupError:
        raise HTTPException(status_code=404)

    if message not in set(user.sent_messages + user.received_messages):
        raise HTTPException(status_code=403)

    msg_db.mark_read(db, message)

    return {
        'valid': True,
        'data': {
            'sender': message.sender.username,
            'receiver': message.receiver.username,
            'body': message.body,
            'replies': [reply.id for reply in msg_db.get_replies(db, message)],
            'replyingTo': message.replying_id,
            'timestamp': adapt_timestamp(message.sent_time.timestamp()),
            'id': message.id,
            'read': message.is_read
        }
    }


@router.get('/delete', summary="Delete the message")
@limiter.limit("1/second")
def messages_delete(request: Request, db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(auth_bearer)], id: Annotated[int, Depends(get_id)]):
    try:
        message = msg_db.get_message(db, id)
    except LookupError:
        raise HTTPException(status_code=404)

    if message not in user.sent_messages:
        raise HTTPException(status_code=403)

    msg_db.delete_message(db, message)


@router.get('/list', summary="Get all sent and received messages")
def messages_list(user: Annotated[models.User, Depends(auth_bearer)], count: int = -1, offset: int = 0, descending: bool = True):
    messages = list(set(user.sent_messages + user.received_messages))
    messages.sort(key=msg_db.get_message_timestamp, reverse=descending)

    return {
        'valid': True,
        'data': [{
            'sender': message.sender.username,
            'receiver': message.receiver.username,
            'partialBody': message.body[:MESSAGE_PREVIEW_BODY_LEN],
            'timestamp': adapt_timestamp(message.sent_time.timestamp()),
            'replyingTo': message.replying_id,
            'id': message.id,
            'read': message.is_read
        } for message in messages[offset:(count + offset) if count != -1 else None] if not message.is_deleted]
    }


def _get_thread_root(db: Session, message: models.Message) -> models.Message:
    return _get_thread_root(db, msg_db.get_message(db, reply_id)) if (reply_id := message.replying_id) else message


def _expand_message_replies(db: Session, user: models.User, message: models.Message) -> dict:
    return {
        'sender': message.sender.username,
        'receiver': message.receiver.username,
        'partialBody': message.body[:MESSAGE_PREVIEW_BODY_LEN],
        'replies': [_expand_message_replies(db, user, reply) for reply in msg_db.get_replies(db, message) if reply in set(user.sent_messages + user.received_messages)],
        'replyingTo': message.replying_id,
        'timestamp': adapt_timestamp(message.sent_time.timestamp()),
        'id': message.id,
    }


@router.get('/thread', summary="Get the thread")
def messages_thread(db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(auth_bearer)], id: Annotated[int, Depends(get_id)]):
    message = msg_db.get_message(db, id)

    if message not in set(user.sent_messages + user.received_messages):
        raise HTTPException(status_code=403)

    root_message = _get_thread_root(db, message)
    thread = _expand_message_replies(db, user, root_message)

    return {
        'valid': True,
        'data': thread
    }
