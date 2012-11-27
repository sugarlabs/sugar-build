import fnmatch
import os
import multiprocessing
import shutil
import sys
import subprocess

from devbot import command
from devbot import config
from devbot import environ
from devbot import state

def unlink_libtool_files():
    def func(arg, dirname, fnames):
        for fname in fnmatch.filter(fnames, "*.la"):
            os.unlink(os.path.join(dirname, fname))

    os.path.walk(config.lib_dir, func, None)

def pull_git_module(module):
    module_dir = module.get_source_dir()

    if os.path.exists(module_dir):
        os.chdir(module_dir)

        command.run(["git", "remote", "set-url", "origin", module.repo])
        command.run(["git", "remote", "update", "origin"], retry=10)
    else:
        os.chdir(config.get_source_dir())
        command.run(["git", "clone", "--progress", module.repo, module.name],
                    retry=10)
        os.chdir(module_dir)

    command.run(["git", "checkout", module.branch])

def pull_module(module):
    print "\n=== Pulling %s ===\n" % module.name

    try:
        pull_git_module(module)
    except subprocess.CalledProcessError:
        sys.exit(1)

def build_make(module):
    command.run(["make"])

def build_autotools(module):
    makefile_path = os.path.join(module.get_build_dir(), "Makefile")

    if not os.path.exists(makefile_path):
        autogen = os.path.join(module.get_source_dir(), "autogen.sh")

        args = [autogen,
                "--prefix", config.prefix_dir,
                "--libdir", config.lib_dir]
        args.extend(module.options)

        command.run(args)

    jobs = multiprocessing.cpu_count() * 2

    command.run(["make", "-j", "%d" % jobs])
    command.run(["make", "install"])

    unlink_libtool_files()

def build_activity(module):
    command.run(["./setup.py", "install", "--prefix", config.prefix_dir])

def build_module(module):
    print "\n=== Building %s ===\n" % module.name

    module_source_dir = module.get_source_dir()

    if module.out_of_source:
        module_build_dir = module.get_build_dir()

        if not os.path.exists(module_build_dir):
            os.mkdir(module_build_dir)

        os.chdir(module_build_dir)
    else:
        os.chdir(module_source_dir)

    try:
        if os.path.exists(os.path.join(module_source_dir, "setup.py")):
            build_activity(module)
        elif os.path.exists(os.path.join(module_source_dir, "autogen.sh")):
            build_autotools(module)
        elif os.path.exists(os.path.join(module_source_dir, "Makefile")):
            build_make(module)
        else:
            raise RuntimeError("Unknown build system")
    except subprocess.CalledProcessError:
        sys.exit(1)

    state.touch_built_commit_id(module)

def rmtree(dir):
    print "Deleting %s" % dir
    shutil.rmtree(dir, ignore_errors=True)

def build_one(module_name):
    environ.setup()

    for module in config.load_modules():
        if module.name == module_name:
            build_module(module)

def pull_one(module_name):
    environ.setup()

    for module in config.load_modules():
        if module.name == module_name:
            pull_module(module)

def pull():
    environ.setup()

    for module in config.load_modules():
        pull_module(module)

def build():
    environ.setup()

    modules = config.load_modules()
    skipped = []

    for module in modules[:]:
        old_commit_id = state.get_built_commit_id(module)
        new_commit_id = module.get_commit_id()

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
        build_module(module)

def clean():
    rmtree(config.install_dir)
    rmtree(config.prefix_dir)
    rmtree(config.get_build_dir())

    for module in config.load_modules():
        if not module.out_of_source:
            rmtree(module.get_source_dir())
