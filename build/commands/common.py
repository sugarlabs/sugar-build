import os
import sys

build_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
root_dir = os.path.dirname(build_dir)

from osbuild import main


def is_buildbot():
    return "SUGAR_BUILDBOT" in os.environ


def get_config_args(log_name=None):
    config_args = {"config_dir": os.path.join(build_dir, "config"),
                   "install_dir": os.path.join(build_dir, "out", "install"),
                   "source_dir": os.path.join(root_dir),
                   "docs_dir": os.path.join(build_dir, "out", "docs"),
                   "state_dir": os.path.join(build_dir, "state"),
                   "prefs_path": os.path.join(root_dir, "prefs"),
                   "logs_dir": os.path.join(build_dir, "logs")}

    if log_name:
        config_args["log_name"] = log_name

    if is_buildbot():
        config_args["git_user_name"] = "buildbot"
        config_args["git_email"] = "buildbot@sugarlabs.org"

    return config_args


def setup(log_name=None, check_args={}):
    config_args = get_config_args(log_name)

    if is_buildbot():
        check_args["interactive"] = False

    if not main.setup(config_args, check_args):
        sys.exit(1)
