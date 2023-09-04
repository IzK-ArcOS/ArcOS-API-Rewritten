import json
from dataclasses import dataclass
from os import PathLike
from pathlib import Path

from sqlalchemy.orm import Session
from ..davult.crud import user as user_db

SHARED_FOLDER_NAME = Path("|Shared|")


@dataclass
class _SharedFolder:
    read_only: list[int]
    full: list[int]

    @staticmethod
    def parse(db: Session, raw: str):
        read_only: list[int] = []
        full: list[int] = []

        def decomment(entry: str) -> str:
            return entry[:i if (i := entry.find('#')) != -1 else None]

        def subparse(db: Session, entry: str, by_id: bool) -> int | None:
            return (user_db.get_user(db, int(entry[1:])) if by_id else user_db.find_user(db, entry)).id

        for entry in [decomment(line).strip() for line in raw.splitlines()]:
            def parse(entry: str, by_id: bool | None = None) -> int:
                nonlocal db

                return subparse(db, entry, by_id if by_id is not None else entry[0] == '|')

            read_only_entry = False

            match entry[0]:
                case '\\':  # escaped
                    user_id = parse(entry[1:], False)
                case '!':
                    read_only_entry = True
                    user_id = parse(entry[1:])
                case _:
                    user_id = parse(entry)

            if read_only_entry:
                read_only.append(user_id)
            else:
                full.append(user_id)

        return _SharedFolder(read_only, full)


@dataclass
class ShareIndex:
    _share_index_storage: Path
    users: dict[int, dict[str, _SharedFolder]]

    def list_shared(self, user_id: int) -> list[int]:
        sharing_users: list[int] = []

        for sharing_user, paths in self.users.items():
            for path, meta in paths.items():
                if user_id in meta.full or user_id in meta.read_only:
                    sharing_users.append(int(sharing_user))
                    break

        return sharing_users

    def register(self, db: Session, user_id: int, path: str, data: str):
        if user_id not in self.users:
            self.users[user_id] = {}

        self.users[user_id][path] = _SharedFolder.parse(db, data)

        self.save_game_progress_in_slot_1()

    def to_json(self) -> str:
        return json.dumps({
            user_id: {
                path: {
                    'read_only': meta.read_only,
                    'full': meta.full
                } for path, meta in path.items()
            } for user_id, path in self.users.items()
        })

    @staticmethod
    def from_json(storage_path: PathLike | str, json_: str):
        return ShareIndex(Path(storage_path), {
            user_id: {
                path: _SharedFolder(**meta)
                for path, meta in shared.items()
            }
            for user_id, shared in json.loads(json_).items()
        })

    def save_game_progress_in_slot_1(self):
        Path(self._share_index_storage).write_text(self.to_json())
