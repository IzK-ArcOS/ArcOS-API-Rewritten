from os import PathLike
from pathlib import Path
import shutil

import magic


class Filesystem:
    _root: Path
    _template: Path | None
    _userspace_size: int

    def __init__(self, root_path: PathLike | str, template_path: PathLike | str | None, userspace_size: int):
        self._root = Path(root_path)
        self._template = Path(template_path)
        self._userspace_size = userspace_size

        self._root.mkdir(parents=True, exist_ok=True)
        self._template.mkdir(parents=True, exist_ok=True)

    def get_userspace_size(self):
        return self._userspace_size

    def get_root(self):
        return self._root

    def get_template_path(self):
        return self._template

    def mkdir(self, path: PathLike | str):
        self._root.joinpath(path).mkdir(exist_ok=True)

    def listdir(self, path: PathLike | str):
        files, directories = [], []

        path = self._root.joinpath(path)
        for child in path.iterdir():
            if child.is_file():
                files.append(child)
            elif child.is_dir():
                directories.append(child)

        return files, directories

    def write(self, path: PathLike | str, data: bytes):
        if self.get_size('.') + len(data) > self._userspace_size:
            raise RuntimeError("data is too large (not enough space)")

        self._root.joinpath(path).write_bytes(data)

    def remove(self, path: PathLike | str):
        path = self._root.joinpath(path)
        if path.is_dir():
            path.rmdir()
        else:
            path.unlink()

    def move(self, source: PathLike | str, destination: PathLike | str):
        shutil.move(self._root.joinpath(source),
                    self._root.joinpath(destination))

    def copy(self, source: PathLike | str, destination: PathLike | str):
        shutil.copy(self._root.joinpath(source),
                    self._root.joinpath(destination))

    def read(self, path: PathLike | str) -> bytes:
        return self._root.joinpath(path).read_bytes()

    def get_size(self, path: PathLike | str) -> int:
        path = self._root.joinpath(path)

        if path.is_file():
            return path.stat().st_size

        directory_size = 0

        for child in path.rglob("*"):
            directory_size += child.stat().st_size

        return directory_size

    def get_mime(self, path: PathLike | str) -> str:
        return magic.from_file(self._root.joinpath(path), mime=True)

    def get_tree(self, path: PathLike | str):
        return list(filter(lambda path: not path.is_dir(), self._root.joinpath(path).rglob("*")))

    def get_stat(self, path: PathLike | str):
        return self._root.joinpath(path).stat()

    def deploy_template(self, path: PathLike | str):
        if self._template is None:
            return

        shutil.copy(self._template, self._root.joinpath(path))
