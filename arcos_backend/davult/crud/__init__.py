from sqlalchemy.orm import Session

from ..database import LocalSession


class CRUD:
    _db: Session

    def __init__(self):
        self._db = LocalSession()

    def __del__(self):
        self._db.close()
