import os
import sys

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(base_dir)

from devbot import main


def setup(log_name=None, check_args={}):
    is_buildbot = "SUGAR_BUILDBOT" in os.environ

    config_args = {"config_dir": os.path.join(base_dir, "config"),
                   "install_dir": os.path.join(base_dir, "install"),
                   "source_dir": os.path.join(base_dir, "source"),
                   "build_dir": os.path.join(base_dir, "build"),
                   "state_dir": os.path.join(base_dir, "state"),
                   "prefs_path": os.path.join(base_dir, "prefs"),
                   "logs_dir": os.path.join(base_dir, "logs"),
                   "relocatable": is_buildbot}

    if log_name:
        config_args["log_name"] = log_name

    if is_buildbot:
        check_args["interactive"] = False

    if not main.setup(config_args, check_args):
        sys.exit(1)
