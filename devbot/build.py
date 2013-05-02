import fnmatch
import re
import os
import multiprocessing
import shutil
import subprocess
from distutils.sysconfig import parse_makefile

from devbot import command
from devbot import config
from devbot import state
from devbot import utils
from devbot import git

_builders = {}
_distributors = {}


def build_one(module_name):
    for module in config.load_modules():
        if module.name == module_name:
            return _build_module(module)

    return False


def pull_one(module_name):
    for module in config.load_modules():
        if module.name == module_name:
            return _pull_module(module)

    return False


def pull(revisions={}, lazy=False):
    to_pull = []
    for module in config.load_modules():
        git_module = git.get_module(module)
        if not lazy or not os.path.exists(git_module.local):
            to_pull.append(module)

    if to_pull:
        print("\n= Pulling =\n")

    for module in to_pull:
        revision = revisions.get(module.name, None)
        if not _pull_module(module, revision):
            return False

    return True


def build(full=False):
    to_build = []
    for module in config.load_modules():
        if not state.built_module_is_unchanged(module):
            to_build.append(module)

    if not to_build:
        return True

    print("\n= Building =\n")

    _ccache_reset()

    for module in to_build:
        if not _build_module(module):
            return False

    _ccache_print_stats()

    return True


def distribute():
    for module in config.load_modules():
        if module.distribute:
            if not _distribute_module(module):
                break

    return True


def clean():
    print("* Emptying install directory")
    _empty_dir(config.install_dir)

    print("* Emptying build directory")
    _empty_dir(config.get_build_dir())

    for module in config.load_modules():
        if not module.out_of_source:
            if git.get_module(module).clean():
                print("* Cleaning %s" % module.name)


def _ccache_reset():
    subprocess.check_call(["ccache", "-z"], stdout=utils.devnull)


def _ccache_print_stats():
    print("\n= ccache statistics =\n")
    subprocess.check_call(["ccache", "-s"])


def _unlink_libtool_files():
    def func(arg, dirname, fnames):
        for fname in fnmatch.filter(fnames, "*.la"):
            os.unlink(os.path.join(dirname, fname))

    os.path.walk(config.lib_dir, func, None)


def _pull_module(module, revision=None):
    print("* Pulling %s" % module.name)

    git_module = git.get_module(module)

    try:
        git_module.update(revision)
    except subprocess.CalledProcessError:
        return False

    return True


def _eval_option(option):
    return eval(option, {"prefix": config.prefix_dir})


def _build_autotools(module, log):
    # Workaround for aclocal 1.11 (fixed in 1.12)
    aclocal_path = os.path.join(config.share_dir, "aclocal")
    utils.ensure_dir(aclocal_path)

    makefile_path = os.path.join(module.get_build_dir(), "Makefile")

    if not os.path.exists(makefile_path):
        configure = os.path.join(module.get_source_dir(), "autogen.sh")
        if not os.path.exists(configure):
            configure = os.path.join(module.get_source_dir(), "configure")

        args = [configure,
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

_builders["autotools"] = _build_autotools


def _build_distutils(module, log):
    setup = os.path.join(module.get_source_dir(), "setup.py")
    command.run(["python", setup, "install", "--prefix",
                 config.prefix_dir], log)

_builders["distutils"] = _build_distutils


def _distribute_autotools(module):
    makefile = parse_makefile("Makefile")
    filename = makefile["DIST_ARCHIVES"]
    version = makefile["VERSION"]

    git_module = git.get_module(module)

    version_revision = None
    description = git_module.describe()
    if description != "v%s" % version:
        match = re.match(r"(v[\d\.]+)", description)
        if match is None:
            print("No version tag was found")
            return False
        else:
            version_revision = match.groups()[0]

    if version_revision is not None:
        git_module.checkout(version_revision)

    return command.run(["make", "distcheck"])

_distributors["autotools"] = _distribute_autotools


def _build_module(module, log=None):
    print("* Building %s" % module.name)

    source_dir = module.get_source_dir()

    if not os.path.exists(source_dir):
        print("Source directory does not exist. Please pull the sources "
              "before building.")
        return False

    if module.out_of_source:
        build_dir = module.get_build_dir()

        if not os.path.exists(build_dir):
            os.mkdir(build_dir)

        os.chdir(build_dir)
    else:
        os.chdir(source_dir)

    try:
        build_system = module.get_build_system()
        if build_system is None:
            return False

        _builders[build_system](module, log)
    except subprocess.CalledProcessError:
        return False

    state.built_module_touch(module)

    return True


def _distribute_module(module, log=None):
    print("\n=== Distribute %s ===\n" % module.name)

    build_dir = module.get_build_dir()

    if not os.path.exists(build_dir):
        print("Build directory does not exist. Please build before "
              "distributing.")
        return False

    os.chdir(build_dir)

    try:
        build_system = module.get_build_system()
        if build_system is None:
            return False

        _distributors[build_system](module)
    except subprocess.CalledProcessError:
        return False

    return True


def _empty_dir(dir_path):
    shutil.rmtree(dir_path, ignore_errors=True)
    os.mkdir(dir_path)
