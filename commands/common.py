import os
import sys

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(base_dir)

from devbot import config
from devbot import command

def setup():
    args = {"config_dir": os.path.join(base_dir, "config"),
            "install_dir": os.path.join(base_dir, "install"),
            "source_dir": os.path.join(base_dir, "source"),
            "build_dir": os.path.join(base_dir, "build"),
            "state_dir": os.path.join(base_dir, "state"),
            "prefs_path": os.path.join(base_dir, "prefs"),
            "logs_dir": os.path.join(base_dir, "logs")}

    if "SUGAR_BUILDBOT" in os.environ:
        args["relocatable"] = True
        args["extra_packages_files"] = ["buildslave.json"]

    config.setup(**args)

    tools_dir = os.path.join(base_dir, "tools")
    command.set_logger(os.path.join(tools_dir, "log-command"))
