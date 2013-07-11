import logging
import os
import sys


build_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
commands_dir = os.path.join(build_dir, "commands")
logs_dir = os.path.join(build_dir, "logs")
root_dir = os.path.dirname(build_dir)
log_path = os.path.join(logs_dir, "main.log")

from osbuild import main
from osbuild import environ


def is_buildbot():
    return "SUGAR_BUILDBOT" in os.environ


def get_config_args():
    config_args = {"config_dir": os.path.join(build_dir),
                   "install_dir": os.path.join(build_dir, "out", "install"),
                   "source_dir": os.path.join(root_dir),
                   "docs_dir": os.path.join(build_dir, "out", "docs"),
                   "dist_dir": os.path.join(build_dir, "out", "dist"),
                   "state_dir": os.path.join(build_dir, "state"),
                   "prefs_path": os.path.join(root_dir, "prefs.json"),
                   "interactive": not is_buildbot()}

    if is_buildbot():
        config_args["git_user_name"] = "buildbot"
        config_args["git_email"] = "buildbot@sugarlabs.org"

    return config_args


def print_close_message():
    print "Type Shift-Alt-Q inside sugar to close."


def setup_logging():
    try:
        os.makedirs(logs_dir)
    except OSError:
        pass

    logging.basicConfig(level=logging.DEBUG,
                        filename=log_path)


def setup():
    setup_logging()

    os.environ["SUGAR_DEVELOPER"] = "1"

    config_args = get_config_args()

    if not main.setup(config_args):
        sys.exit(1)

    environ.add_path("PATH", os.path.join(commands_dir, "broot"))


def run(command):
    setup()
    if not getattr(main, "cmd_%s" % command)():
        sys.exit(1)
