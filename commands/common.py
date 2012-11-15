import os
import sys

base_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(base_path)

from devbot import system
from devbot import config

def setup():
    config.set_config_dir(os.path.join(base_path, "config"))
    config.set_install_dir(os.path.join(base_path, "install"))
    config.set_source_dir(os.path.join(base_path, "source"))
    config.set_build_dir(os.path.join(base_path, "build"))
