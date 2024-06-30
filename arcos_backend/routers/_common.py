from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..davult.database import LocalSession


# TODO move into davult
def get_db() -> Session:
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


def _verify_user_new_prop(init: dict, data: dict) -> None:
    if (acc := data.get('acc')) is not None:
        if not isinstance(acc, dict):
            raise HTTPException(status_code=422)

        if any(map(lambda k: init['acc'][k] != acc[k], filter(lambda s: s in acc and s in init['acc'], ('enabled', 'admin')))):
            raise HTTPException(status_code=403)
