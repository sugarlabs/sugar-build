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

def load_packages():
    return _load_deps_json("packages-%s" % distro.get_system_version())

def load_prerequisites():
    return _load_deps_json("prerequisites")

def load_checks():
    version = distro.get_system_version()

    checks = []
    checks.extend(_load_deps_json("system"))
    checks.extend(_load_deps_json("sugar-build"))
    checks.extend(_load_deps_json("sugar-buildtime-%s" % version))
    checks.extend(_load_deps_json("sugar-runtime-%s" % version))

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

