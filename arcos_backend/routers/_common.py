from sqlalchemy.orm import Session

from ..davult.database import LocalSession


# TODO move into davult
def get_db() -> Session:
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
