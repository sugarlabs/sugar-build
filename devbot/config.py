import json
import os

from devbot import distro

config_dir = None
logs_dir = None
commands_dir = None
install_dir = None
source_dir = None
build_dir = None
lib_dir = None
devbot_dir = None
share_dir = None
bin_dir = None
etc_dir = None
dep_files = None
module_files = None
package_files = None
use_lib64 = os.uname()[4] == "x86_64"

if use_lib64:
    system_lib_dir = "/usr/lib64"
else:
    system_lib_dir = "/usr/lib"

def set_config_dir(dir):
    global config_dir
    config_dir = dir

def set_logs_dir(dir):
    global logs_dir
    logs_dir = dir

def set_install_dir(dir):
    global install_dir
    global devbot_dir
    global share_dir
    global bin_dir
    global etc_dir
    global lib_dir

    install_dir = dir
    devbot_dir = os.path.join(install_dir, "devbot")
    share_dir = os.path.join(install_dir, "share")
    bin_dir = os.path.join(install_dir, "bin")
    etc_dir = os.path.join(install_dir, "etc")

    if use_lib64:
        lib_dir = os.path.join(install_dir, "lib64")
    else:
        lib_dir = os.path.join(install_dir, "lib")

def set_source_dir(dir):
    global source_dir
    source_dir = dir

def set_build_dir(dir):
    global build_dir
    build_dir = dir

def set_commands_dir(dir):
    global commands_dir
    commands_dir = dir

def set_dep_files(files):
    global dep_files
    dep_files = files

def set_module_files(files):
    global module_files
    module_files = files

def set_package_files(files):
    global package_files
    package_files = files

def get_module_source_dir(module):
    return os.path.join(source_dir, module["name"])

def get_module_build_dir(module):
    return os.path.join(build_dir, module["name"])

def load_packages():
    packages = []
    for package_file in package_files:
        packages.extend(_load_deps_json(package_file))

def load_prerequisites():
    return _load_deps_json("prerequisites")

def load_checks():
    version = distro.get_system_version()

    checks = []
    for check_file in dep_files:
        checks.extend(_load_deps_json(check_file))

    return checks

def load_modules():
    version = distro.get_system_version()

    module_files = ["system-%s.json" % version,
                    "sugar.json",
                    "activities.json"]

    modules = []

    for module_file in module_files:
        path = os.path.join(config_dir, "modules", module_file)
        modules.extend(json.load(open(path)))

    return modules

def _load_deps_json(name):
    path = os.path.join(config_dir, "deps", "%s.json" % name)
    return json.load(open(path))

