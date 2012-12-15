import os
import sys

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
tests_dir = os.path.join(base_dir, "tests")

sys.path.append(base_dir)

from devbot import config
from devbot import command

def setup():
    relocatable = "SUGAR_BUILDBOT" in os.environ
    logs_dir = os.path.join(base_dir, "logs")
    install_dir = os.path.join(base_dir, "install")
    tools_dir = os.path.join(base_dir, "tools")

    config.setup(devbot_dir=os.path.join(base_dir, "devbot"),
                 config_dir=os.path.join(base_dir, "config"),
                 install_dir=install_dir,
                 source_dir=os.path.join(base_dir, "source"),
                 build_dir=os.path.join(base_dir, "build"),
                 commands_dir=os.path.join(base_dir, "commands"),
                 home_dir=os.path.join(base_dir, "home"),
                 prefs_path=os.path.join(base_dir, "prefs"),
                 logs_dir=logs_dir,
                 relocatable=relocatable)

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

    command.set_logger(os.path.join(tools_dir, "log-command"))
