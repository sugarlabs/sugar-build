import os
import subprocess

from devbot import command
from devbot import utils
from devbot import config

_root_path = None


def _chdir(func):
    def wrapped(*args, **kwargs):
        orig_cwd = os.getcwd()

        os.chdir(args[0].local)
        result = func(*args, **kwargs)
        os.chdir(orig_cwd)

        return result

    return wrapped


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

        if self.tag:
            command.run(["git", "checkout", self.tag])
        else:
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
                         "origin/%s" % self._branch])

    @_chdir
    def checkout(self, revision=None):
        if revision is None:
            revision = self.tag
            if revision is None:
                revision = self._branch

        command.run(["git", "checkout", revision])

    @_chdir
    def describe(self):
        return subprocess.check_output(["git", "describe"]).strip()

    @_chdir
    def is_valid(self):
        result = subprocess.call(["git", "rev-parse", "HEAD"],
                                 stdout=utils.devnull,
                                 stderr=utils.devnull)
        return result == 0

    @_chdir
    def get_commit_id(self):
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()

    @_chdir
    def get_annotation(self, tag):
        # FIXME this is fragile, there must be a better way

        show = subprocess.check_output(["git", "show", tag])

        annotation = []
        for line in show.split("\n"):
            ignore = False
            for start in ["tag ", "Tagger: ", "Date: "]:
                if line.startswith(start):
                    ignore = True

            if line.startswith("commit "):
                break

            if not ignore:
                annotation.append(line)

        return "\n".join(annotation)

    def clean(self):
        try:
            os.chdir(self.local)
        except OSError:
            return False

        command.run(["git", "clean", "-fdx"])

        return True


def set_root_path(path):
    global _root_path
    _root_path = path


def get_module(module):
    return Module(path=config.get_source_dir(),
                  name=module.name,
                  remote=module.repo,
                  branch=module.branch,
                  tag=module.tag,
                  retry=10)


def get_root_module():
    remote = "git://git.sugarlabs.org/sugar-build/sugar-build.git"

    module = Module(name=os.path.basename(_root_path),
                    remote=remote,
                    path=os.path.dirname(_root_path))
    if not module.is_valid():
        return None

    return module
