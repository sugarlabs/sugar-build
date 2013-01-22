import os
import subprocess

from devbot import config
from devbot import command
from devbot import xvfb
from devbot import build


def check_one(module_name):
    for module in config.load_modules():
        if module.name == module_name:
            return _check_module(module)

    return False


def check():
    if not build.build():
        return False

    modules = config.load_modules()
    for module in modules:
        if not _check_module(module):
            return False

    return True


def _check_module(module):
    result = True

    if module.has_checks:
        print("* Checking %s" % module.name)

        os.chdir(module.get_build_dir())

        xvfb_proc, orig_display = xvfb.start()

        try:
            command.run(["make", "check"])
        except subprocess.CalledProcessError:
            result = False

        xvfb.stop(xvfb_proc, orig_display)

    return result
