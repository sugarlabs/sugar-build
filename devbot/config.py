import imp
import json
import os
import pkgutil
import tempfile

from devbot import distro
from devbot import utils
from devbot import plugins
from devbot import git

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
libexec_dir = None
dep_files = None
package_files = None
system_lib_dirs = None
cache_home_dir = None
config_home_dir = None
data_home_dir = None
build_state_dir = None

_source_dir = None
_build_dir = None
_prefs_path = None

class Module:
    def __init__(self, info):
        self.name = info["name"]
        self.repo = info["repo"]
        self.branch = info.get("branch", "master")
        self.tag = info.get("tag", None)
        self.auto_install = info.get("auto-install", False)
        self.options = info.get("options", [])
        self.options_evaluated = info.get("options_evaluated", [])
        self.has_tests = info.get("has_tests", False)

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

    def get_git_module(self):
        return git.Module(path=get_source_dir(), name=self.name,
                          remote=self.repo, branch=self.branch, tag=self.tag,
                          retry=10)

def _ensure_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)

def get_commit_id():
    commit_id = utils.get_commit_id(config_dir)
    if commit_id is None:
        commit_id = "snapshot"

    return commit_id

def setup(**kwargs):
    _load_plugins()

    global devbot_dir
    devbot_dir = kwargs["devbot_dir"]

    global config_dir
    config_dir = kwargs["config_dir"]

    global logs_dir
    logs_dir = kwargs["logs_dir"]
    _ensure_dir(logs_dir)

    global commands_dir
    commands_dir = kwargs["commands_dir"]

    global _prefs_path
    _prefs_path = kwargs["prefs_path"]

    global _source_dir
    _source_dir = kwargs["source_dir"]

    global _build_dir
    _build_dir = kwargs["build_dir"]

    _setup_state_dir(kwargs["state_dir"])
    _setup_install_dir(kwargs["install_dir"], kwargs["relocatable"])

def _setup_state_dir(state_dir):
    _ensure_dir(state_dir)

    global build_state_dir
    build_state_dir = os.path.join(state_dir, "build")
    _ensure_dir(build_state_dir)

    home_dir = os.path.join(state_dir, "home")
    _ensure_dir(home_dir)

    global cache_home_dir
    cache_home_dir = os.path.join(home_dir, "cache")
    _ensure_dir(cache_home_dir)

    global config_home_dir
    config_home_dir = os.path.join(home_dir, "config")
    _ensure_dir(config_home_dir)

    global data_home_dir
    data_home_dir = os.path.join(home_dir, "data")
    _ensure_dir(data_home_dir)

def _setup_prefix_dir(dir, relocatable):
    global prefix_dir

    real_prefix_path = os.path.join(build_state_dir, "real_prefix")

    if os.path.exists(real_prefix_path):
        with open(real_prefix_path) as f:
            prefix_dir = f.read()
    elif relocatable:
        tmp_dir = tempfile.mkdtemp(prefix="sugar-build")
        prefix_dir = os.path.join(tmp_dir, "install")
        with open(real_prefix_path, "w") as f:
            f.write(prefix_dir)
    else:
        prefix_dir = dir
        return

    tmp_dir = os.path.dirname(prefix_dir)
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    if os.path.islink(prefix_dir):
        os.remove(prefix_dir)
    os.symlink(dir, prefix_dir)

def _setup_install_dir(dir, relocatable=False):
    global system_lib_dirs
    global install_dir
    global prefix_dir
    global share_dir
    global bin_dir
    global etc_dir
    global lib_dir
    global libexec_dir

    install_dir = dir
    _ensure_dir(install_dir)

    _setup_prefix_dir(dir, relocatable)

    share_dir = os.path.join(prefix_dir, "share")
    _ensure_dir(share_dir)
    _ensure_dir(os.path.join(share_dir, "aclocal"))

    bin_dir = os.path.join(prefix_dir, "bin")
    etc_dir = os.path.join(prefix_dir, "etc")
    libexec_dir = os.path.join(prefix_dir, "libexec")

    distro_info = distro.get_distro_info()

    relative_lib_dir = distro_info.lib_dir
    if relative_lib_dir is None:
        relative_lib_dir = "lib"

    lib_dir = os.path.join(prefix_dir, relative_lib_dir)

    system_lib_dirs = ["/usr/lib"]
    if distro_info.lib_dir is not None:
        system_lib_dirs.append(os.path.join("/usr", distro_info.lib_dir))

def get_source_dir():
    global _source_dir
    _ensure_dir(_source_dir)
    return _source_dir

def get_build_dir():
    global _build_dir
    _ensure_dir(_build_dir)
    return _build_dir

def set_dep_files(files):
    global dep_files
    dep_files = files

def set_package_files(files):
    global package_files
    package_files = files

def _read_prefs():
    global _prefs_path

    if _prefs_path is None or not os.path.exists(_prefs_path):
        return {}

    prefs = {}
    with open(_prefs_path) as f:
        for line in f.readlines():
            splitted = line.strip().split("=")
            if len(splitted) == 2:
                prefs[splitted[0]] = splitted[1]

    return prefs

def _save_prefs(prefs):
    global _prefs_path

    if _prefs_path is None:
        return

    with open(_prefs_path, "w") as f:
        for pref in prefs.items():
            f.write("%s\n" % "=".join(pref))

def get_log_path(prefix):
    logfile_path = None
    number = 0

    while logfile_path is None:
        name = "%s-%d.log" % (prefix, number)
        path = os.path.join(logs_dir, name)

        if not os.path.exists(path):
            logfile_path = path

        number = number + 1

    return logfile_path

def get_pref(name):
    prefs = _read_prefs()
    return prefs.get(name, None)

def set_pref(name, value):
    prefs = _read_prefs()
    prefs[name] = value
    _save_prefs(prefs)

def _load_plugins():
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

def _filter_if(item):
    if "if" not in item:
        return True

    distro_info = distro.get_distro_info()
    globals = { "gstreamer_version": distro_info.gstreamer_version,
                "gnome_version": distro_info.gnome_version }

    return eval(item["if"], globals)

def load_checks():
    checks = []
    for file in dep_files:
        path = os.path.join(config_dir, "deps", "%s.json" % file)
        checks.extend(json.load(open(path)))

    return filter(_filter_if, checks)

def load_modules():
    module_dir = os.path.join(config_dir, "modules")

    modules = []
    with open(os.path.join(module_dir, "index.json")) as f:
        for module_file in json.load(f):
            path = os.path.join(module_dir, module_file)
            for info in json.load(open(path)):
                modules.append(info)

    return [Module(info) for info in filter(_filter_if, modules)]

def clean():
    try:
        os.rmdir(logs_dir)
    except OSError:
        pass
