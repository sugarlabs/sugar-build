import imp
import json
import os
import pkgutil
import tempfile

from devbot import distro
from devbot import utils
from devbot import plugins

devbot_dir = None
config_dir = None
logs_dir = None
commands_dir = None
install_dir = None
prefix_dir = None
lib_dir = None
share_dir = None
bin_dir = None
etc_dir = None
home_dir = None
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

    def get_commit_id(self):
        if not os.path.exists(self.get_source_dir()):
            return None

        return utils.get_commit_id(self.get_source_dir())

def _ensure_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)

def get_commit_id():
    commit_id = utils.get_commit_id(config_dir)
    if commit_id is None:
        commit_id = "snapshot"

    return commit_id

def set_devbot_dir(dir):
    global devbot_dir
    devbot_dir = dir

def set_config_dir(dir):
    global config_dir
    config_dir = dir

def set_logs_dir(dir):
    global logs_dir
    logs_dir = dir
    _ensure_dir(logs_dir)

def set_home_dir(dir):
    global home_dir
    home_dir = dir
    _ensure_dir(home_dir)

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
    global share_dir
    global bin_dir
    global etc_dir
    global lib_dir

    install_dir = dir
    _ensure_dir(install_dir)

    prefix_dir = _get_prefix_dir(dir, relocatable)

    share_dir = os.path.join(prefix_dir, "share")
    _ensure_dir(share_dir)
    _ensure_dir(os.path.join(share_dir, "aclocal"))

    bin_dir = os.path.join(prefix_dir, "bin")
    etc_dir = os.path.join(prefix_dir, "etc")

    if distro.get_distro_info().use_lib64:
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

def _read_prefs():
    global prefs_path

    if not os.path.exists(prefs_path):
        return {}

    prefs = {}
    with open(prefs_path) as f:
        for line in f.readlines():
            splitted = line.strip().split("=")
            if len(splitted) == 2:
                prefs[splitted[0]] = splitted[1]

    return prefs

def _save_prefs(prefs):
    global prefs_path

    with open(prefs_path, "w") as f:
        for pref in prefs.items():
            f.write("%s\n" % "=".join(pref))

def get_pref(name):
    prefs = _read_prefs()
    return prefs.get(name, None)

def set_pref(name, value):
    prefs = _read_prefs()
    prefs[name] = value
    _save_prefs(prefs)

def load_plugins():
    for loader, name, ispkg in pkgutil.iter_modules(plugins.__path__):
        f, filename, desc = imp.find_module(name, plugins.__path__)
        imp.load_module(name, f, filename, desc)

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
    version = distro.get_distro_info().system_version

    checks = []
    for file in dep_files:
        path = os.path.join(config_dir, "deps", "%s.json" % file)
        checks.extend(json.load(open(path)))

    return checks

def load_modules():
    version = distro.get_distro_info().system_version

    module_files = ["system-%s.json" % version,
                    "sugar.json",
                    "activities.json"]

    modules = []

    for file in module_files:
        path = os.path.join(config_dir, "modules", file)

        for info in json.load(open(path)):
            modules.append(Module(info))

    return modules

def clean():
    try:
        os.rmdir(home_dir)
        os.rmdir(logs_dir)
    except OSError:
        pass
