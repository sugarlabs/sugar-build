import os
import sys

base_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(base_path)

from devbot import system
from devbot import config
from devbot import distro

def setup():
    config.set_config_dir(os.path.join(base_path, "config"))
    config.set_install_dir(os.path.join(base_path, "install"))
    config.set_source_dir(os.path.join(base_path, "source"))
    config.set_build_dir(os.path.join(base_path, "build"))
    config.set_commands_dir(os.path.join(base_path, "commands"))
    config.set_logs_dir(os.path.join(base_path, "logs"))

    version = distro.get_system_version()

    module_files = ["system-%s.json" % version,
                    "sugar.json",
                    "activities.json"]

    config.set_module_files(module_files)

    dep_files = ["system",
                 "sugar-build",
                 "sugar-buildtime-%s" % version,
                 "sugar-runtime-%s" % version]

    config.set_dep_files(dep_files)

    package_files = ["packages-%s" % version]

    config.set_package_files(package_files)
