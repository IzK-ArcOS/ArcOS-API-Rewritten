import json
import os
import shutil

import magic


class Filesystem:
    _root: str
    _template: str | None
    _userspace_size: int

    def __init__(self, root_path: str, template_path: str | None, userspace_size: int):
        self._root = root_path
        self._template = template_path
        self._userspace_size = userspace_size

        os.makedirs(self._root, exist_ok=True)

    def get_userspace_size(self):
        return self._userspace_size

    def get_root(self):
        return self._root

    def get_template_path(self):
        return self._template

    def mkdir(self, path: str):
        os.mkdir(os.path.join(self._root, path))

    def listdir(self, path: str):
        path = self._adapt(path)
        files, directories = [], []

        for felder in os.listdir(path):
            fullpath = os.path.join(path, felder)
            if os.path.isfile(fullpath):
                files.append(fullpath)
            else:
                directories.append(fullpath)

        return files, directories

    def write(self, path: str, data: bytes):
        if self.get_size('.') + len(data) > self._userspace_size:
            raise RuntimeError("data is too large (not enough space)")

        with open(os.path.join(self._root, path), 'wb') as f:
            f.write(data)


    def remove(self, path: str):
        path = os.path.join(self._root, path)

        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.unlink(path)

    def move(self, source: str, destination: str):
        shutil.move(os.path.join(self._root, source),
                    os.path.join(self._root, destination))

    def read(self, path: str) -> bytes:
        with open(os.path.join(self._root, path), 'rb') as f:
            return f.read()

    def get_size(self, path: str) -> int:
        internal_path = os.path.join(self._root, path)

        if os.path.isfile(internal_path):
            return os.path.getsize(internal_path)

        directory_size = 0

        for dirpath, _, files in os.walk(internal_path):
            if not files:
                continue

            subdirectory_size = 0

            for file in files:
                subdirectory_size += os.path.getsize(os.path.join(dirpath, file))

            directory_size += subdirectory_size

        return directory_size

    def get_mime(self, path: str) -> str:
        return magic.from_file(os.path.join(self._root, path), mime=True)

    def get_tree(self, path: str):
        base_path = self._root

        paths = []
        for dirpath, _, filepaths in os.walk(os.path.join(base_path, path)):
            paths.extend([os.path.join(dirpath[len(base_path) + 1:], filepath) for filepath in filepaths])

        return paths

    def deploy_template(self, path: str):
        if self._template is None:
            return

        for (parent, folders, files) in os.walk(self._template, followlinks=True):
            fullpath = parent[len(self._template) + 1:]
            for folder in folders:
                self.mkdir(os.path.join(path, fullpath, folder))
            for file in files:
                with open(os.path.join(parent, file), 'rb') as f:
                    self.write(os.path.join(path, fullpath, file), f.read())

    def _adapt(self, path: str) -> str:
        return os.path.normpath(os.path.join(self._root, path))
