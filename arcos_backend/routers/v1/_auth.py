import base64

from fastapi import HTTPException

from ..._shared import database as db


def basic(credentials: str) -> tuple[str, str]:
    if not credentials.startswith('Basic '):
        raise HTTPException(status_code=422, detail="invalid authorization method")

    username, password = base64.b64decode(credentials[6:]).decode('utf-8').split(':')

    return username, password


def bearer(token: str) -> int:
    if not token.startswith('Bearer '):
        raise HTTPException(status_code=422, detail="invalid authorization method")

    user_id = db.validate_token(token[7:])

    if user_id is None:
        raise HTTPException(status_code=403)

    return user_id
