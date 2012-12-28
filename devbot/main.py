import pkgutil
import imp

from devbot import config
from devbot import environ
from devbot import plugins
from devbot import system
from devbot import build
from devbot import state
from devbot import clean


def run_build(full=False):
    if full or state.full_build_is_required():
        clean.clean(build_only=True)
        environ.setup_gconf()

    state.full_build_touch()

    if not system.check(lazy=True):
        return False

    if not build.pull(lazy=True):
        return False

    if not build.build(full=False):
        return False

    return True


def load_plugins():
    for loader, name, ispkg in pkgutil.iter_modules(plugins.__path__):
        f, filename, desc = imp.find_module(name, plugins.__path__)
        imp.load_module(name, f, filename, desc)


def setup(config_args):
    load_plugins()

    config.setup(**config_args)

    environ.setup_variables()
    environ.setup_gconf()
