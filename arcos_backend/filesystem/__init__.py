import os


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

    def write(self, userspace: int, path: str, data: bytes):
        with open(os.path.join(self._root, str(userspace), path), 'wb') as f:
            f.write(data)

    def read(self, userspace: int, path: str) -> bytes:
        with open(os.path.join(self._root, str(userspace), path), 'rb') as f:
            return f.read()

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
