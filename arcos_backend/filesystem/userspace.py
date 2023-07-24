import os

from arcos_backend import Filesystem


class Userspace:
    _id: int
    _fs: Filesystem
    _root: str

    def __init__(self, fs: Filesystem, id: int):
        self._fs = fs
        self._id = id
        self._root = os.path.join(self._fs.get_root(), str(id))

        if not os.path.isdir(self._root):
            os.mkdir(self._root)
            self.deploy_template('.')

    def get_root(self):
        return self._root

    def delete(self):
        self._fs.remove(str(self._id))

    def mkdir(self, path: str):
        self._validate(path)
        self._fs.mkdir(self._adapt(path))

    def listdir(self, path: str):
        self._validate(path)
        files, directories = self._fs.listdir(self._adapt(path))

        files = [self._scope(file) for file in files]
        directories = [self._scope(directory) for directory in directories]

        return files, directories

    def write(self, path: str, data: bytes):
        self._validate(path)
        self._fs.write(self._adapt(path), data)

    def remove(self, path: str):
        self._validate(path)
        self._fs.remove(self._adapt(path))

    def move(self, source: str, destination: str):
        self._validate(source)
        self._validate(destination)
        self._fs.move(self._adapt(source), self._adapt(destination))

    def copy(self, source: str, destination: str):
        self._validate(source)
        self._validate(destination)
        self._fs.copy(self._adapt(source), self._adapt(destination))

    def read(self, path: str) -> bytes:
        self._validate(path)
        return self._fs.read(self._adapt(path))

    def get_size(self, path: str) -> int:
        self._validate(path)
        return self._fs.get_size(self._adapt(path))

    def get_mime(self, path: str) -> str:
        self._validate(path)
        return self._fs.get_mime(self._adapt(path))

    def get_tree(self, path: str):
        self._validate(path)
        return [path[path.find(os.sep) + 1:] for path in self._fs.get_tree(self._adapt(path))]

    def deploy_template(self, path: str):
        self._validate(path)
        self._fs.deploy_template(self._adapt(path))

    def _scope(self, path: os.PathLike) -> str:
        path = str(path)
        path = path[path.find('/') + 1:]
        return path[path.find('/') + 1:]

    def _adapt(self, path: str) -> str:
        return os.path.normpath(os.path.join(str(self._id), path))

    def _validate(self, path: str):
        userspace_root = os.path.abspath(self._root)
        requested_path = os.path.abspath(os.path.join(userspace_root, path))

        if not requested_path.startswith(userspace_root):
            raise ValueError("path breaks out of the filesystem")
