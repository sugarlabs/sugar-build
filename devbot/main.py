import pkgutil
import imp

from devbot import config
from devbot import environ
from devbot import plugins


def load_plugins():
    for loader, name, ispkg in pkgutil.iter_modules(plugins.__path__):
        f, filename, desc = imp.find_module(name, plugins.__path__)
        imp.load_module(name, f, filename, desc)


def setup(config_args):
    load_plugins()
    config.setup(**config_args)
    environ.setup()
