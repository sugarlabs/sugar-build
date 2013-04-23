import json
import os
import tempfile

from devbot import distro
from devbot import utils

config_dir = None
logs_dir = None
install_dir = None
prefix_dir = None
lib_dir = None
share_dir = None
bin_dir = None
etc_dir = None
libexec_dir = None
package_files = None
system_lib_dirs = None
home_dir = None
build_state_dir = None
log_path = None

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
        self.has_checks = info.get("has_checks", False)
        self.distribute = info.get("distribute", False)

        if get_pref("BUILD_IN_SOURCE"):
            self.out_of_source = False
        else:
            self.out_of_source = info.get("out-of-source", True)

    def get_source_dir(self):
        return os.path.join(get_source_dir(), self.name)

    def get_build_dir(self):
        return os.path.join(get_build_dir(), self.name)

    def get_build_system(self):
        source_dir = self.get_source_dir()
        if os.path.exists(os.path.join(source_dir, "setup.py")):
            return "activity"
        elif os.path.exists(os.path.join(source_dir, "autogen.sh")) or \
             os.path.exists(os.path.join(source_dir, "configure")):
            return "autotools"
        else:
            print("The source directory has unexpected content, please "
                  "delete it and pull\nthe source again.")
            return None


def setup(**kwargs):
    global config_dir
    config_dir = kwargs.get("config_dir", None)

    global logs_dir
    logs_dir = kwargs["logs_dir"]
    utils.ensure_dir(logs_dir)

    global _prefs_path
    _prefs_path = kwargs.get("prefs_path", None)

    global _source_dir
    _source_dir = kwargs["source_dir"]

    global _build_dir
    _build_dir = kwargs["build_dir"]

    relocatable = kwargs.get("relocatable", False)

    _setup_state_dir(kwargs["state_dir"])
    _setup_install_dir(kwargs["install_dir"], relocatable)

    global log_path
    if "log_name" in kwargs:
        log_path = _create_log(kwargs["log_name"])


def get_source_dir():
    global _source_dir
    utils.ensure_dir(_source_dir)
    return _source_dir


def get_build_dir():
    global _build_dir
    utils.ensure_dir(_build_dir)
    return _build_dir


def get_pref(name):
    defaults = {"PROFILE": "default"}

    prefs = _read_prefs()
    return prefs.get(name, defaults.get(name, None))


def set_pref(name, value):
    prefs = _read_prefs()
    prefs[name] = value
    _save_prefs(prefs)


def get_full_build():
    config = None
    with open(os.path.join(config_dir, "config.json")) as f:
        config = json.load(f)

    return config["full_build"]


def load_packages():
    packages = {}

    for path in _read_index("packages"):
        packages.update(json.load(open(path)))

    return packages


def load_prerequisites():
    path = os.path.join(config_dir, "deps", "prerequisites.json")
    return json.load(open(path))


def load_checks():
    checks = []
    for path in _read_index("deps"):
        checks.extend(json.load(open(path)))

    return filter(_filter_if, checks)


def load_modules():
    modules = []
    for path in _read_index("modules"):
        for info in json.load(open(path)):
            modules.append(info)

    return [Module(info) for info in filter(_filter_if, modules)]


def _create_log(prefix):
    logfile_path = None
    number = 0

    while logfile_path is None:
        name = "%s-%d.log" % (prefix, number)
        path = os.path.join(logs_dir, name)

        if not os.path.exists(path):
            logfile_path = path

        number = number + 1

    link_path = os.path.join(logs_dir, "%s.log" % prefix)

    try:
        os.unlink(link_path)
    except OSError:
        pass

    os.symlink(logfile_path, link_path)

    return logfile_path


def _filter_if(item):
    if "if" not in item:
        return True

    distro_info = distro.get_distro_info()
    globals = {"gstreamer_version": distro_info.gstreamer_version,
               "gnome_version": distro_info.gnome_version,
               "distro": "%s-%s" % (distro_info.name, distro_info.version)}

    return eval(item["if"], globals)


def _read_index(dir_name):
    if config_dir is None:
        return []

    index_dir = os.path.join(config_dir, dir_name)
    with open(os.path.join(index_dir, "index.json")) as f:
        return [os.path.join(index_dir, json_file)
                for json_file in json.load(f)]


def _setup_state_dir(state_dir):
    utils.ensure_dir(state_dir)

    global build_state_dir
    build_state_dir = os.path.join(state_dir, "build")
    utils.ensure_dir(build_state_dir)

    base_home_dir = os.path.join(state_dir, "home")
    utils.ensure_dir(base_home_dir)

    global home_dir
    home_dir = os.path.join(base_home_dir, get_pref("PROFILE"))
    utils.ensure_dir(home_dir)


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
    utils.ensure_dir(install_dir)

    _setup_prefix_dir(dir, relocatable)

    share_dir = os.path.join(prefix_dir, "share")
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
