import base64
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request

from ._common import auth_bearer, adapt_timestamp, get_msg_db, get_user_db
from ...davult import models, schemas
from ...davult.crud.message import MessageDB
from ...davult.crud.user import UserDB


MESSAGE_PREVIEW_BODY_LEN = 30


router = APIRouter()


def get_id(id: str) -> int:
    return int(base64.b64decode(id).decode('utf-8'))


def get_target(user_db: Annotated[UserDB, Depends(get_user_db)], target: str) -> models.User:
    return user_db.find_user(base64.b64decode(target).decode('utf-8'))


@router.post('/send')
async def messages_send(request: Request, msg_db: Annotated[MessageDB, Depends(get_msg_db)], user: Annotated[models.User, Depends(auth_bearer)], target: Annotated[models.User, Depends(get_target)]):
    try:
        message = msg_db.send_message(schemas.MessageCreate(
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


@router.post('/reply')
async def messages_reply(request: Request, msg_db: Annotated[MessageDB, Depends(get_msg_db)], user: Annotated[models.User, Depends(auth_bearer)], id: int, target: Annotated[models.User, Depends(get_target)]):
    try:
        message = msg_db.send_message(schemas.MessageCreate(
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


@router.get('/get')
def messages_get(msg_db: Annotated[MessageDB, Depends(get_msg_db)], user: Annotated[models.User, Depends(auth_bearer)], id: Annotated[int, Depends(get_id)]):
    try:
        message = msg_db.get_message(id)
    except LookupError:
        raise HTTPException(status_code=404)

    if message not in set(user.sent_messages + user.received_messages):
        raise HTTPException(status_code=403)

    msg_db.mark_read(message)

    return {
        'valid': True,
        'data': {
            'sender': message.sender.username,
            'receiver': message.receiver.username,
            'body': message.body,
            'replies': [reply.id for reply in msg_db.get_replies(message)],
            'replyingTo': message.replying_id,
            'timestamp': adapt_timestamp(message.sent_time.timestamp()),
            'id': message.id,
            'read': message.is_read
        }
    }


@router.get('/delete')
def messages_delete(msg_db: Annotated[MessageDB, Depends(get_msg_db)], user: Annotated[models.User, Depends(auth_bearer)], id: Annotated[int, Depends(get_id)]):
    try:
        message = msg_db.get_message(id)
    except LookupError:
        raise HTTPException(status_code=404)

    if message not in user.sent_messages:
        raise HTTPException(status_code=403)

    msg_db.delete_message(message)


@router.get('/list')
def messages_get(user: Annotated[models.User, Depends(auth_bearer)]):
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
        } for message in set(user.sent_messages + user.received_messages) if not message.is_deleted]
    }


def _get_thread_root(msg_db: MessageDB, message: models.Message) -> models.Message:
    return _get_thread_root(msg_db, msg_db.get_message(reply_id)) if (reply_id := message.replying_id) else message


def _expand_message_replies(msg_db: MessageDB, user: models.User, message: models.Message) -> dict:
    return {
        'sender': message.sender.username,
        'receiver': message.receiver.username,
        'partialBody': message.body[:MESSAGE_PREVIEW_BODY_LEN],
        'replies': [_expand_message_replies(user, reply) for reply in msg_db.get_replies(message) if reply in set(user.sent_messages + user.received_messages) and (msg_db.get_replies(reply) or not reply.is_deleted)],
        'replyingTo': message.replying_id,
        'timestamp': adapt_timestamp(message.sent_time.timestamp()),
        'id': message.id,
    }


@router.get('/thread')
def messages_thread(msg_db: Annotated[MessageDB, Depends(get_msg_db)], user: Annotated[models.User, Depends(auth_bearer)], id: Annotated[int, Depends(get_id)]):
    message = msg_db.get_message(id)

    if message not in set(user.sent_messages + user.received_messages):
        raise HTTPException(status_code=403)

    root_message = _get_thread_root(msg_db, message)
    thread = _expand_message_replies(msg_db, user, root_message)

    return {
        'valid': True,
        'data': thread
    }
