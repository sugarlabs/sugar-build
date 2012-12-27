import os
import subprocess

from devbot import config
from devbot import environ
from devbot import command
from devbot import xvfb


def test_one(module_name):
    environ.setup()

    for module in config.load_modules():
        if module.name == module_name:
            return _test_module(module)

    return False


def test():
    environ.setup()

    modules = config.load_modules()
    for module in modules:
        if not _test_module(module):
            return False

    return True


def _test_module(module):
    result = True

    if module.has_tests:
        os.chdir(module.get_build_dir())

        xvfb_proc, orig_display = xvfb.start()

        try:
            command.run(["make", "check"])
        except subprocess.CalledProcessError:
            result = False

        xvfb.stop(xvfb_proc, orig_display)

    return result
