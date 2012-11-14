import os
import sys

base_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(base_path)

from devbot import system
from devbot import config

def setup():
    config.set_path(os.path.join(base_path, "scripts", "deps"))
