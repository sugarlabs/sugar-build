import os
import sys

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(base_dir)

from devbot import config
from devbot import command

def setup():
    config.setup(config_dir=os.path.join(base_dir, "config"),
                 install_dir=os.path.join(base_dir, "install"),
                 source_dir=os.path.join(base_dir, "source"),
                 build_dir=os.path.join(base_dir, "build"),
                 state_dir=os.path.join(base_dir, "state"),
                 prefs_path=os.path.join(base_dir, "prefs"),
                 logs_dir=os.path.join(base_dir, "logs"),
                 relocatable="SUGAR_BUILDBOT" in os.environ)

    dep_files = ["system",
                 "sugar-build",
                 "sugar-buildtime",
                 "sugar-runtime"]

    config.set_dep_files(dep_files)

    package_files = ["basesystem",
                     "deps"]

    if "SUGAR_BUILDBOT" in os.environ:
        package_files.append("buildslave")

    config.set_package_files(package_files)

    tools_dir = os.path.join(base_dir, "tools")
    command.set_logger(os.path.join(tools_dir, "log-command"))
