import os
import sys

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
tests_dir = os.path.join(base_dir, "tests")

sys.path.append(base_dir)

from devbot import system
from devbot import config
from devbot import distro
from devbot import command

def setup():
    config.load_plugins()

    relocatable = "SUGAR_BUILDBOT" in os.environ
    logs_dir = os.path.join(base_dir, "logs")
    install_dir = os.path.join(base_dir, "install")
    tools_dir = os.path.join(base_dir, "tools")

    config.set_devbot_dir(os.path.join(base_dir, "devbot"))
    config.set_config_dir(os.path.join(base_dir, "config"))
    config.set_install_dir(install_dir, relocatable=relocatable)
    config.set_source_dir(os.path.join(base_dir, "source"))
    config.set_build_dir(os.path.join(base_dir, "build"))
    config.set_commands_dir(os.path.join(base_dir, "commands"))
    config.set_home_dir(os.path.join(base_dir, "home"))
    config.set_prefs_path(os.path.join(base_dir, "prefs"))
    config.set_logs_dir(logs_dir)

    os.environ["SB_LOGS_DIR"] = logs_dir
    os.environ["SB_LIBEXEC_DIR"] = config.libexec_dir

    version = distro.get_distro_info().system_version

    module_files = ["system-%s.json" % version,
                    "sugar.json",
                    "activities.json"]

    config.set_module_files(module_files)

    dep_files = ["system",
                 "sugar-build",
                 "sugar-buildtime-%s" % version,
                 "sugar-runtime-%s" % version]

    config.set_dep_files(dep_files)

    package_files = ["basesystem",
                     "deps-%s" % version]

    if "SUGAR_BUILDBOT" in os.environ:
        package_files.append("buildslave")

    config.set_package_files(package_files)

    command.set_logger(os.path.join(tools_dir, "log-command"))
