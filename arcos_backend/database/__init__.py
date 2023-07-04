import json
import os.path
import sqlite3
import threading
import time
import uuid

from ._utils import hash_salty
from .._validation import validate_username


DEFAULT_PROPERTIES = {'sh': {'taskbar': {'centered': False, 'labels': False, 'pos': '', 'docked': True}, 'window': {'lefttb': False, 'bigtb': True, 'buttons': 'default'}, 'desktop': {'wallpaper': 'img04', 'icons': True, 'theme': 'dark', 'sharp': False, 'accent': '70D6FF'}, 'start': {'small': True}, 'anim': True, 'noQuickSettings': False, 'noGlass': False, 'userThemes': {}}, 'acc': {'enabled': True, 'admin': False, 'profilePicture': 3}, 'volume': {'level': 100, 'muted': False}, 'disabledApps': [], 'autoRun': [], 'autoLoads': [], 'askPresist': True, 'devmode': False, 'appdata': {}}


class Database:
    _connection: sqlite3.Connection
    _lock: threading.Lock

    def __init__(self, db_path: str):
        if not os.path.isfile(db_path):
            with open(db_path, 'wb'): pass  # NOQA E701

        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._lock = threading.Lock()

        self._create_default()

    def create_user(self, username: str, password: str):
        if not validate_username(username):
            raise ValueError("invalid username")

        with self._lock:
            self._connection.execute("INSERT INTO Users(Name, PasswordHash) VALUES (?,?)", (username, hash_salty(password)))
            self._connection.commit()

    def rename_user(self, user_id: int, new_name: str):
        with self._lock:
            self._connection.execute("UPDATE Users SET Name=(?) WHERE ID=(?)", (new_name, user_id))
            self._connection.commit()

    def delete_user(self, user_id: int):
        with self._lock:
            self._connection.execute("DELETE FROM Users WHERE ID=(?)", (user_id,))
            self._connection.commit()

    def set_user_password(self, user_id: int, password: str):
        with self._lock:
            self._connection.execute("UPDATE Users Set PasswordHash=(?) WHERE ID=(?)", (hash_salty(password), user_id))
            self._connection.commit()

    def set_user_properties(self, user_id: int, properties: dict):
        properties_data = json.JSONEncoder().encode(properties)

        with self._lock:
            self._connection.execute("UPDATE Users SET Properties=(?) WHERE ID=(?)", (properties_data, user_id))
            self._connection.commit()

    def get_user_ids(self) -> list[int]:
        with self._lock:
            user_ids = self._connection.execute("SELECT ID FROM Users").fetchall()

        return [user_id[0] for user_id in user_ids]

    def find_user(self, username: str) -> int:
        with self._lock:
            return self._connection.execute("SELECT ID FROM Users WHERE Name=(?)", (username,)).fetchone()[0]

    def get_username(self, user_id: int) -> int:
        with self._lock:
            return self._connection.execute("SELECT Name FROM Users WHERE ID=(?)", (user_id,)).fetchone()[0]

    def get_user_info(self, user_id: int) -> dict:
        with self._lock:
            information = self._connection.execute("SELECT Name, Properties, ProfilePicture, IsEnabled, IsAdmin FROM Users WHERE ID=(?)", (user_id,)).fetchone()

        username, properties_data, pfp, enabled, admin = information
        properties = json.JSONDecoder().decode(properties_data)

        return {
            'username': username,
            'account': {
                'enabled': enabled,
                'admin': admin,
                'profile_picture': pfp,
                'properties': properties
            }
        }

    def validate_user_credentials(self, username: str, password: str) -> bool:
        with self._lock:
            if self._connection.execute("SELECT ID FROM Users WHERE Name=(?) AND PasswordHash=(?)", (username, hash_salty(password))).fetchone():
                return True
            else:
                return False

    def generate_token(self, username: str, password: str, life_time: int | None) -> str:
        if not self.validate_user_credentials(username, password):
            raise ValueError("invalid credentials")

        token = str(uuid.uuid4())
        user_id = self.find_user(username)

        expires = 'null'
        if life_time is not None:
            expires = round(time.time() + life_time)

        with self._lock:
            self._connection.execute("INSERT INTO Tokens(Value, User, Expires) VALUES (?,?,?)", (token, user_id, expires))
            self._connection.commit()

        return token

    def validate_token(self, token: str) -> int | None:
        with self._lock:
            token_info = self._connection.execute("SELECT User, Expires FROM Tokens WHERE Value=(?)", (token,)).fetchone()

        if token_info is None:
            return None

        owner_id, expires = token_info

        if time.time() > expires:
            self.expire_token(token)
            return None

        return owner_id

    def expire_token(self, token: str):
        with self._lock:
            self._connection.execute("DELETE FROM Tokens WHERE Value=(?)", (token,))
            self._connection.commit()

    def _create_default(self):
        with self._lock:
            # users
            self._connection.execute("CREATE TABLE IF NOT EXISTS Users("
                                     "ID INTEGER PRIMARY KEY ASC AUTOINCREMENT NOT NULL,"
                                     "Name TEXT UNIQUE NOT NULL,"
                                     "PasswordHash TEXT NOT NULL,"
                                     f"Properties TEXT DEFAULT '{json.JSONEncoder().encode(DEFAULT_PROPERTIES)}',"
                                     "ProfilePicture TEXT DEFAULT '3',"
                                     "IsEnabled BOOLEAN NOT NULL CHECK ( IsEnabled IN (0, 1) ) DEFAULT 1,"
                                     "IsAdmin BOOLEAN NOT NULL CHECK ( IsEnabled IN (0, 1) ) DEFAULT 0);")

            # tokens
            self._connection.execute("CREATE TABLE IF NOT EXISTS Tokens("
                                     "Value TEXT PRIMARY KEY NOT NULL,"
                                     "User INTEGER NOT NULL,"
                                     "Expires INTEGER,"
                                     "FOREIGN KEY(User) REFERENCES Users(ID))")

            # messages
            self._connection.execute("CREATE TABLE IF NOT EXISTS Messages("
                                     "ID INTEGER PRIMARY KEY ASC AUTOINCREMENT,"
                                     "Sender INTEGER REFERENCES Users(ID) NOT NULL,"
                                     "Receiver INTEGER REFERENCES Users(ID) NOT NULL,"
                                     "Body TEXT NOT NULL,"
                                     "Timestamp INTEGER NOT NULL,"
                                     "ReplyingTo INTEGER REFERENCES Messages(ID))")

            self._connection.commit()
