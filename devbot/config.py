import json
import os
import tempfile

from devbot import distro

config_dir = None
logs_dir = None
commands_dir = None
install_dir = None
prefix_dir = None
lib_dir = None
devbot_dir = None
share_dir = None
bin_dir = None
etc_dir = None
dep_files = None
module_files = None
package_files = None
prefs_path = None

_source_dir = None
_build_dir = None

class Module:
    def __init__(self, info):
        self.name = info["name"]
        self.repo = info["repo"]
        self.branch = info.get("branch", "master")
        self.auto_install = info.get("auto-install", False)
        self.options = info.get("options", [])

        if get_pref("BUILD_IN_SOURCE"):
            self.out_of_source = False
        else:
            self.out_of_source = info.get("out-of-source", True)

    def get_source_dir(self):
        return os.path.join(get_source_dir(), self.name)

    def get_build_dir(self):
        return os.path.join(get_build_dir(), self.name)

def _ensure_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)

def set_config_dir(dir):
    global config_dir
    config_dir = dir

def set_logs_dir(dir):
    global logs_dir
    logs_dir = dir

def _get_prefix_dir(dir, relocatable):
    real_prefix_path = os.path.join(dir, "real_prefix")

    if os.path.exists(real_prefix_path):
        with open(real_prefix_path) as f:
            prefix_dir = f.read()
    elif relocatable:
        tmp_dir = tempfile.mkdtemp(prefix="sugar-build")
        prefix_dir = os.path.join(tmp_dir, "install")
        with open(real_prefix_path, "w") as f:
            f.write(prefix_dir)
    else:
        return dir

    tmp_dir = os.path.dirname(prefix_dir)
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    if os.path.islink(prefix_dir):
        os.remove(prefix_dir)
    os.symlink(dir, prefix_dir)

    return prefix_dir

def set_install_dir(dir, relocatable=False):
    global system_lib_dir
    global install_dir
    global prefix_dir
    global devbot_dir
    global share_dir
    global bin_dir
    global etc_dir
    global lib_dir

    install_dir = dir
    _ensure_dir(install_dir)

    prefix_dir = _get_prefix_dir(dir, relocatable)

    devbot_dir = os.path.join(prefix_dir, "devbot")
    _ensure_dir(devbot_dir)

    share_dir = os.path.join(prefix_dir, "share")
    _ensure_dir(share_dir)
    _ensure_dir(os.path.join(share_dir, "aclocal"))

    bin_dir = os.path.join(prefix_dir, "bin")
    etc_dir = os.path.join(prefix_dir, "etc")

    if distro.get_use_lib64():
        lib_dir = os.path.join(prefix_dir, "lib64")
        system_lib_dir = "/usr/lib64"
    else:
        lib_dir = os.path.join(prefix_dir, "lib")
        system_lib_dir = "/usr/lib"

def set_source_dir(dir):
    global _source_dir
    _source_dir = dir

def set_build_dir(dir):
    global _build_dir
    _build_dir = dir

def get_source_dir():
    global _source_dir
    _ensure_dir(_source_dir)
    return _source_dir

def get_build_dir():
    global _build_dir
    _ensure_dir(_build_dir)
    return _build_dir

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
