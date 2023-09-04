from os import PathLike
from pathlib import Path

from sqlalchemy.orm import Session

from arcos_backend import Filesystem


# TODO make it inherit `Filesystem` instead
class Userspace:
    _id: int
    _fs: Filesystem
    _path_id: Path
    _root: Path

    def __init__(self, fs: Filesystem, id: int):
        self._fs = fs
        self._id = id
        self._path_id = Path(str(id))
        self._root = self._fs.get_root().joinpath(str(id))

        if not self._root.exists():
            self._root.mkdir(parents=True)
            self.deploy_template('.')

    def get_root(self):
        return self._root

    def delete(self):
        self._fs.remove(str(self._id))

    def mkdir(self, path: PathLike | str):
        self._validate(path)
        self._fs.mkdir(self._path_id.joinpath(path))

    def listdir(self, path: PathLike | str):
        self._validate(path)
        files, directories = self._fs.listdir(self._path_id.joinpath(path))

        files = [self._scope(file) for file in files]
        directories = [self._scope(directory) for directory in directories]

        return files, directories

    def write(self, db: Session, path: PathLike | str, data: bytes):
        self._validate(path)
        self._fs.write(db, self._path_id.joinpath(path), data)

    def remove(self, path: PathLike | str):
        self._validate(path)
        self._fs.remove(self._path_id.joinpath(path))

    def move(self, source: PathLike | str, destination: PathLike | str):
        self._validate(source, destination)
        self._fs.move(self._path_id.joinpath(source),
                      self._path_id.joinpath(destination))

    def copy(self, source: PathLike | str, destination: PathLike | str):
        self._validate(source, destination)
        self._fs.copy(self._path_id.joinpath(source),
                      self._path_id.joinpath(destination))

    def read(self, path: PathLike | str) -> bytes:
        self._validate(path)
        return self._fs.read(self._path_id.joinpath(path))

    def get_size(self, path: PathLike | str) -> int:
        self._validate(path)
        return self._fs.get_size(self._path_id.joinpath(path))

    def get_mime(self, path: PathLike | str) -> str:
        self._validate(path)
        return self._fs.get_mime(self._path_id.joinpath(path))

    def get_tree(self, path: PathLike | str):
        self._validate(path)
        return [self._scope(path, 4) for path in self._fs.get_tree(self._path_id.joinpath(path))]

    def get_stat(self, path: PathLike | str):
        self._validate(path)
        return self._fs.get_stat(self._path_id.joinpath(path))

    def deploy_template(self, path: PathLike | str):
        self._validate(path)
        self._fs.deploy_template(self._path_id.joinpath(path))

    @staticmethod
    def _scope(path: PathLike | str, level: int = 2):
        return (path := Path(path)).relative_to(path.parents[-level])

    def _validate(self, *paths: PathLike | str):
        for path in paths:
            requested_path = self._root.joinpath(path)
            if not requested_path.resolve().is_relative_to(self._root.absolute()):
                raise ValueError("path breaks out of the filesystem")
