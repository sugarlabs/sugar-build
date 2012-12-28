import os
import sys

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(base_dir)

from devbot import config
from devbot import git


def setup(log_name=None):
    args = {"config_dir": os.path.join(base_dir, "config"),
            "install_dir": os.path.join(base_dir, "install"),
            "source_dir": os.path.join(base_dir, "source"),
            "build_dir": os.path.join(base_dir, "build"),
            "state_dir": os.path.join(base_dir, "state"),
            "prefs_path": os.path.join(base_dir, "prefs"),
            "logs_dir": os.path.join(base_dir, "logs")}

    if log_name:
        args["log_name"] = log_name

    if "SUGAR_BUILDBOT" in os.environ:
        args["relocatable"] = True

    config.setup(**args)
