import os

from devbot import command

class Module:
    def __init__(self, path, name, remote, branch="master", tag=None):
        self.remote = remote
        self.local = os.path.join(path, name)
        self.tag = tag

        self._path = path
        self._name = name
        self._branch = branch

    def _clone(self):
        os.chdir(self._path)

        command.run(["git", "clone", "--progress",
                     self.remote, self._name],
                    retry=10)

        os.chdir(self.local)

        command.run(["git", "checkout", self._branch])

    def update(self):
        if not os.path.exists(os.path.join(self.local, ".git")):
            self._clone()
            return

        os.chdir(self.local)

        command.run(["git", "fetch"])

        if self.tag:
            command.run(["git", "checkout", self.tag])
        else:
            command.run(["git", "merge", "origin", self._branch])
