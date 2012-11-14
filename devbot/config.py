import json
import os

from devbot import distro

config_path = None

def set_path(path):
    global config_path
    config_path = path

def load_packages():
    packages = _load_deps_json("packages-%s" % distro.get_system_version())

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

def _load_deps_json(name):
    path = os.path.join(config_path, "%s.json" % name)
    return json.load(open(path))

