import magic
import os
import shutil


class Filesystem:
    _root: str
    _template: str | None
    _userspace_size: int

    def __init__(self, root_path: str, template_path: str | None, userspace_size: int):
        self._root = root_path
        self._template = template_path
        self._userspace_size = userspace_size

        os.makedirs(self._root, exist_ok=True)

    def mkdir(self, userspace: int, path: str):
        os.mkdir(os.path.join(self._root, str(userspace), path))

    def listdir(self, userspace: int, path: str):
        path = os.path.join(self._root, str(userspace), path)

        files, directories = [], []

        for felder in os.listdir(path):
            fullpath = os.path.join(path, felder)
            if os.path.isfile(fullpath):
                files.append(fullpath)
            else:
                directories.append(fullpath)

        return files, directories

    def write(self, userspace: int, path: str, data: bytes):
        with open(os.path.join(self._root, str(userspace), path), 'wb') as f:
            f.write(data)

    def delete(self, userspace: int, path: str):
        shutil.rmtree(os.path.join(self._root, str(userspace), path))

    def move(self, userspace: int, source: str, destination: str):
        base_path = os.path.join(self._root, str(userspace))
        shutil.move(os.path.join(base_path, source),
                    os.path.join(base_path, destination))

    def read(self, userspace: int, path: str) -> bytes:
        with open(os.path.join(self._root, str(userspace), path), 'rb') as f:
            return f.read()

    def get_size(self, userspace: int, path: str) -> int:
        return sum(sum(os.path.getsize(os.path.join(dirpath, file)) for file in files) for dirpath, files, _ in
                   os.walk(walk_path)) \
            if os.path.isdir(walk_path := os.path.join(self._root, str(userspace), path)) else os.path.getsize(
            os.path.join(walk_path))

    def get_mime(self, userspace: int, path: str) -> str:
        return magic.from_file(os.path.join(self._root, str(userspace), path), mime=True)

    def get_tree(self, userspace: int, path: str):
        base_path = os.path.join(self._root, str(userspace))

        paths = []
        for dirpath, _, filepaths in os.walk(os.path.join(base_path, path)):
            paths.extend([os.path.join(dirpath[len(base_path) + 1:], filepath) for filepath in filepaths])

        return paths

    def deploy_template(self, userspace: int, path: str):
        if self._template is None:
            return

        for (parent, folders, files) in os.walk(self._template, followlinks=True):
            fullpath = parent[len(self._template) + 1:]
            for folder in folders:
                self.mkdir(userspace, os.path.join(path, fullpath, folder))
            for file in files:
                with open(os.path.join(parent, file), 'rb') as f:
                    self.write(userspace, os.path.join(path, fullpath, file), f.read())

    def create_userspace(self, userspace: int):
        os.mkdir(os.path.join(self._root, str(userspace)))
        self.deploy_template(userspace, '.')

    def get_basepath(self, userspace: int):
        return os.path.join(self._root, str(userspace))

    def get_userspace_size(self):
        return self._userspace_size

    def copy(self, userspace: int, source: str, target: str):
        self.write(userspace, target, self.read(userspace, source))

    def validate_path(self, userspace: int, path: str) -> bool:
        return os.path.exists(os.path.join(self._root, str(userspace), path))
