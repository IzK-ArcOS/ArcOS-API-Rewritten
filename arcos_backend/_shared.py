from .database import Database
from .filesystem import Filesystem


API_REVISION = 1


configuration: dict = None
database: Database = None
filesystem: Filesystem = None
