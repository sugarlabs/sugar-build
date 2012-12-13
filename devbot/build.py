import fnmatch
import os
import multiprocessing
import shutil
import subprocess

from devbot import command
from devbot import config
from devbot import environ
from devbot import state
from devbot import utils

def build_one(module_name):
    environ.setup()

    for module in config.load_modules():
        if module.name == module_name:
            return _build_module(module)

    return False

def pull_one(module_name):
    environ.setup()

    for module in config.load_modules():
        if module.name == module_name:
            return _pull_module(module)

    return False

def pull():
    environ.setup()

    for module in config.load_modules():
        if not _pull_module(module):
            return False

    return True

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
        if not _build_module(module, config.get_log_path("build")):
            return False

    return True

def clean():
    _rmtree(config.install_dir)
    _rmtree(config.prefix_dir)
    _rmtree(config.get_build_dir())

    for module in config.load_modules():
        if not module.out_of_source:
            if module.get_git_module().clean():
                print "Cleaned %s git repository." % module.name

def _unlink_libtool_files():
    def func(arg, dirname, fnames):
        for fname in fnmatch.filter(fnames, "*.la"):
            os.unlink(os.path.join(dirname, fname))

    os.path.walk(config.lib_dir, func, None)

def _pull_module(module):
    print "\n=== Pulling %s ===\n" % module.name

    try:
        module.get_git_module().update()
    except subprocess.CalledProcessError:
        return False

    return True

def _eval_option(option):
    return eval(option, {"prefix": config.prefix_dir})

def _build_autotools(module, log):
    makefile_path = os.path.join(module.get_build_dir(), "Makefile")

    if not os.path.exists(makefile_path):
        configure = os.path.join(module.get_source_dir(), "configure")
        if not os.path.exists(configure):
            configure = os.path.join(module.get_source_dir(), "autogen.sh")

        args = [configure,
                "--cache-file=/tmp/cache-%s" % module.name,
                "--prefix", config.prefix_dir,
                "--libdir", config.lib_dir]
        args.extend(module.options)

        for option in module.options_evaluated:
            args.append(_eval_option(option))

        command.run(args, log)

    jobs = multiprocessing.cpu_count() * 2

    command.run(["make", "-j", "%d" % jobs], log)
    command.run(["make", "install"], log)

    _unlink_libtool_files()

def _build_activity(module, log):
    setup = os.path.join(module.get_source_dir(), "setup.py")
    command.run([setup, "install", "--prefix", config.prefix_dir], log)

def _build_module(module, log=None):
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
