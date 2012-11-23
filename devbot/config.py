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
prefs_path = None

class Module:
    def __init__(self, info):
        self.name = info["name"]
        self.repo = info["repo"]
        self.branch = info.get("branch", "master")
        self.auto_install = info.get("auto-install", False)

        if get_pref("BUILD_IN_SOURCE"):
            self.out_of_source = False
        else:
            self.out_of_source = info.get("out-of-source", True)

    def get_source_dir(self):
        return os.path.join(source_dir, self.name)

    def get_build_dir(self):
        return os.path.join(build_dir, self.name)

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

    if distro.get_use_lib64():
        lib_dir = os.path.join(install_dir, "lib64")
        system_lib_dir = "/usr/lib64"
    else:
        lib_dir = os.path.join(install_dir, "lib")
        system_lib_dir = "/usr/lib"

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

def set_prefs_path(path):
    global prefs_path
    prefs_path = path

def get_pref(name):
    prefs = {}

    if not os.path.exists(prefs_path):
        return None

    with open(prefs_path) as f:
        for line in f.readlines():
            splitted = line.strip().split("=")
            if len(splitted) == 2:
                prefs[splitted[0]] = splitted[1]

    return prefs.get(name, None)

def load_packages():
    packages = {}

    for file in package_files:
        path = os.path.join(config_dir, "packages", "%s.json" % file)
        packages.update(json.load(open(path)))

    return packages

def load_prerequisites():
    path = os.path.join(config_dir, "deps", "prerequisites.json")
    return json.load(open(path))

def load_checks():
    version = distro.get_system_version()

    checks = []
    for file in dep_files:
        path = os.path.join(config_dir, "deps", "%s.json" % file)
        checks.extend(json.load(open(path)))

    return checks

def load_modules():
    version = distro.get_system_version()

    module_files = ["system-%s.json" % version,
                    "sugar.json",
                    "activities.json"]

    modules = []

    for file in module_files:
        path = os.path.join(config_dir, "modules", file)

        for info in json.load(open(path)):
            modules.append(Module(info))

    return modules
