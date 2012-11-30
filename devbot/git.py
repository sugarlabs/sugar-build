import os

from devbot import command

class Module:
    def __init__(self, path=None, name=None, remote=None,
                 branch="master", tag=None, retry=10):
        if path is None or name is None or remote is None:
            raise RuntimeError("path, name and remote are required")

        self.remote = remote
        self.local = os.path.join(path, name)
        self.tag = tag

        self._path = path
        self._name = name
        self._branch = branch
        self._retry = 10

    def _clone(self):
        os.chdir(self._path)

        command.run(["git", "clone", "--progress", self.remote, self._name],
                    retry=self._retry)

        os.chdir(self.local)

        command.run(["git", "checkout", self._branch])

    def update(self):
        if not os.path.exists(os.path.join(self.local, ".git")):
            self._clone()
            return

        os.chdir(self.local)

        command.run(["git", "fetch"], retry=self._retry)

        if self.tag:
            command.run(["git", "checkout", self.tag])
        else:
            command.run(["git", "merge", "--ff-only",
                         "origin/%s" % self._branch],
                        retry=self._retry)

    def clean(self):
        try:
            os.chdir(self.local)
        except OSError:
            return False

        command.run(["git", "clean", "-fdx"])

        return True
