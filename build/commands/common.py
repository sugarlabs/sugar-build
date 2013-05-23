import logging
from logging.handlers import RotatingFileHandler
import os
import sys

build_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
commands_dir = os.path.join(build_dir, "commands")
logs_dir = os.path.join(build_dir, "logs")
root_dir = os.path.dirname(build_dir)

from osbuild import main
from osbuild import environ


def is_buildbot():
    return "SUGAR_BUILDBOT" in os.environ


def get_config_args():
    config_args = {"config_dir": os.path.join(build_dir, "config"),
                   "install_dir": os.path.join(build_dir, "out", "install"),
                   "source_dir": os.path.join(root_dir),
                   "docs_dir": os.path.join(build_dir, "out", "docs"),
                   "state_dir": os.path.join(build_dir, "state"),
                   "prefs_path": os.path.join(root_dir, "prefs")}

    if is_buildbot():
        config_args["git_user_name"] = "buildbot"
        config_args["git_email"] = "buildbot@sugarlabs.org"

    return config_args


def print_close_message():
    print "Type Shift-Alt-Q inside sugar to close."


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    log_path = os.path.join(logs_dir, "sugar-build.log")

    try:
        os.makedirs(logs_dir)
    except OSError:
        pass

    handler = RotatingFileHandler(log_path, backupCount=10, maxBytes=5242880)
    logger.addHandler(handler)


def setup(check_args={}):
    setup_logging()

    os.environ["SUGAR_DEVELOPER"] = "1"

    config_args = get_config_args()

    if is_buildbot():
        check_args["interactive"] = False

    if not main.setup(config_args, check_args):
        sys.exit(1)

    environ.add_path("PATH", commands_dir)
