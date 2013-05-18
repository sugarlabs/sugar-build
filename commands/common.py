import os
import sys

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(base_dir)

from osbuild import main


def is_buildbot():
    return "SUGAR_BUILDBOT" in os.environ


def setup(log_name=None, check_args={}):
    config_args = {"config_dir": os.path.join(base_dir, "config"),
                   "install_dir": os.path.join(base_dir, "out", "install"),
                   "source_dir": os.path.join(base_dir),
                   "docs_dir": os.path.join(base_dir, "out", "docs"),
                   "state_dir": os.path.join(base_dir, "out", "state"),
                   "prefs_path": os.path.join(base_dir, "prefs"),
                   "logs_dir": os.path.join(base_dir, "out", "logs")}

    if log_name:
        config_args["log_name"] = log_name

    if is_buildbot():
        check_args["interactive"] = False
        config_args["git_user_name"] = "buildbot"
        config_args["git_email"] = "buildbot@sugarlabs.org"

    if not main.setup(config_args, check_args):
        sys.exit(1)
