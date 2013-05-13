import os
import subprocess

from devbot import config
from devbot import command
from devbot import xvfb
from devbot import build

_checkers = {}


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
    if module.has_checks:
        print("* Checking %s" % module.name)
        return _checkers[module.get_build_system()](module)
    return True


def _volo_checker(module):
    orig_root = module.get_source_dir()
    for root, dirs, files in os.walk(module.get_source_dir()):
        if root == orig_root and "lib" in dirs:
            dirs.remove("lib")
        for f in files:
            if f.endswith(".js"):
                try:
                    command.run(["jshint", os.path.join(root, f)])
                except subprocess.CalledProcessError:
                    return False
    return True

_checkers['volo'] = _volo_checker


def _autotools_checker(module):
    result = True
    os.chdir(module.get_build_dir())
    xvfb_proc, orig_display = xvfb.start()

    try:
        command.run(["dbus-launch", "--exit-with-session",
                     "make", "check"])
    except subprocess.CalledProcessError:
        result = False

    xvfb.stop(xvfb_proc, orig_display)

    return result

_checkers['autotools'] = _autotools_checker
