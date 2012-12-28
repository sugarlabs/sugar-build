import hashlib
import os
import json

from devbot import config

_BUILT_MODULES = "builtmodules"
_FULL_BUILD = "fullbuild"
_SYSTEM_CHECK = "syscheck"


def built_module_touch(module):
    built_modules = _load_state(_BUILT_MODULES, {})

    source_hash = _compute_mtime_hash(module.get_source_dir())
    built_modules[module.name] = {"source_hash": source_hash}

    _save_state(_BUILT_MODULES, built_modules)


def built_module_is_unchanged(module):
    built_modules = _load_state(_BUILT_MODULES, {})
    if module.name not in built_modules:
        return False

    built_module = built_modules[module.name]
    if "source_hash" not in built_module:
        return False

    old_source_hash = built_module["source_hash"]
    new_source_hash = _compute_mtime_hash(module.get_source_dir())

    return old_source_hash == new_source_hash


def system_check_is_unchanged():
    system_check = _load_state(_SYSTEM_CHECK)
    if not system_check or not "config_hash" in system_check:
        return False

    config_hash = _compute_mtime_hash(config.config_dir)

    return system_check["config_hash"] == config_hash


def system_check_touch():
    system_check = _load_state(_SYSTEM_CHECK, {})

    config_hash = _compute_mtime_hash(config.config_dir)
    system_check["config_hash"] = config_hash

    _save_state(_SYSTEM_CHECK, system_check)


def full_build_is_required():
    full_build = _load_state(_FULL_BUILD)
    if not full_build:
        return True

    return not (full_build["last"] == config.get_full_build())


def full_build_touch():
    full_build = _load_state(_FULL_BUILD, {})
    full_build["last"] = config.get_full_build()
    _save_state(_FULL_BUILD, full_build)


def clean(build_only=False):
    print "* Deleting state"

    names = [_BUILT_MODULES, _FULL_BUILD]
    if not build_only:
        names.append(_SYSTEM_CHECK)

    for name in names:
        try:
            os.unlink(_get_state_path(name))
        except OSError:
            pass


def _get_state_path(name):
    return os.path.join(config.build_state_dir, "%s.json" % name)


def _load_state(name, default=None):
    state = default

    try:
        with open(_get_state_path(name)) as f:
            state = json.load(f)
    except IOError:
        pass

    return state


def _save_state(name, state):
    with open(_get_state_path(name), "w+") as f:
        json.dump(state, f, indent=4)
        f.write('\n')


def _compute_mtime_hash(path):
    # For some reason if path is unicode we
    # get a 10x slow down for some directories
    path = str(path)

    data = ""
    for root, dirs, files in os.walk(path):
        for name in files:
            path = os.path.join(root, name)
            mtime = os.lstat(path).st_mtime
            data = "%s%s %s\n" % (data, mtime, path)

            if ".git" in dirs:
                dirs.remove(".git")

    return hashlib.sha256(data).hexdigest()
