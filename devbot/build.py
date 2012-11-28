import fnmatch
import os
import multiprocessing
import shutil
import sys
import subprocess
import time

from devbot import command
from devbot import config
from devbot import environ
from devbot import state

def build_one(module_name):
    environ.setup()

    for module in config.load_modules():
        if module.name == module_name:
            _build_module(module)

def pull_one(module_name):
    environ.setup()

    for module in config.load_modules():
        if module.name == module_name:
            _pull_module(module)

def pull():
    environ.setup()

    for module in config.load_modules():
        _pull_module(module)

def build():
    environ.setup()

    modules = config.load_modules()
    skipped = []

    for module in modules[:]:
        new_commit_id = module.get_commit_id()
        if new_commit_id is None:
            break

        old_commit_id = state.get_built_commit_id(module)
        if old_commit_id == new_commit_id:
            modules.pop(0)
            skipped.append(module.name)
        else:
            break

    if skipped:
        print "\n* Skipping unchanged modules *\n"
        print "\n".join(skipped)

    for module in modules:
        state.remove_built_commit_id(module)

    for module in modules:
        log = "build-%s" % time.strftime("%Y%m%d-%H%M%S")
        if not _build_module(module, log):
            break

def clean():
    _rmtree(config.install_dir)
    _rmtree(config.prefix_dir)
    _rmtree(config.get_build_dir())

    for module in config.load_modules():
        if not module.out_of_source:
            _rmtree(module.get_source_dir())

def _unlink_libtool_files():
    def func(arg, dirname, fnames):
        for fname in fnmatch.filter(fnames, "*.la"):
            os.unlink(os.path.join(dirname, fname))

    os.path.walk(config.lib_dir, func, None)

def _pull_git_module(module):
    module_dir = module.get_source_dir()

    if os.path.exists(os.path.join(module_dir, ".git")):
        os.chdir(module_dir)

        command.run(["git", "remote", "set-url", "origin", module.repo])
        command.run(["git", "remote", "update", "origin"], retry=10)
    else:
        os.chdir(config.get_source_dir())
        command.run(["git", "clone", "--progress", module.repo, module.name],
                    retry=10)
        os.chdir(module_dir)

    command.run(["git", "checkout", module.branch])

def _pull_module(module):
    print "\n=== Pulling %s ===\n" % module.name

    try:
        _pull_git_module(module)
    except subprocess.CalledProcessError:
        sys.exit(1)

def _build_make(module, log):
    command.run(["make"], log)

def _build_autotools(module, log):
    makefile_path = os.path.join(module.get_build_dir(), "Makefile")

    if not os.path.exists(makefile_path):
        autogen = os.path.join(module.get_source_dir(), "autogen.sh")

        args = [autogen,
                "--prefix", config.prefix_dir,
                "--libdir", config.lib_dir]
        args.extend(module.options)

        command.run(args, log)

    jobs = multiprocessing.cpu_count() * 2

    command.run(["make", "-j", "%d" % jobs], log)
    command.run(["make", "install"], log)

    _unlink_libtool_files()

def _build_activity(module, log):
    command.run(["./setup.py", "install", "--prefix", config.prefix_dir], log)

def _build_module(module, log):
    print "\n=== Building %s ===\n" % module.name

    source_dir = module.get_source_dir()

    if not os.path.exists(source_dir):
        print "Source directory does not exist. Please pull the sources " \
              "before building."
        return False

    if module.out_of_source:
        build_dir = module.get_build_dir()

        if not os.path.exists(build_dir):
            os.mkdir(build_dir)

        os.chdir(build_dir)
    else:
        os.chdir(source_dir)

    try:
        if os.path.exists(os.path.join(source_dir, "setup.py")):
            _build_activity(module, log)
        elif os.path.exists(os.path.join(source_dir, "autogen.sh")):
            _build_autotools(module, log)
        elif os.path.exists(os.path.join(source_dir, "Makefile")):
            _build_make(module, log)
        else:
            print "The source directory has unexpected content, please " \
                  "delete it and pull\nthe source again."                
            return False
    except subprocess.CalledProcessError:
        return False

    state.touch_built_commit_id(module)

    return True

def _rmtree(dir):
    print "Deleting %s" % dir
    shutil.rmtree(dir, ignore_errors=True)
