import os
import json

from devbot import config

_BUILT_MODULES = "builtmodules"
_SYSTEM_CHECK = "syscheck"

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

def touch_built_module(module):
    built_modules = _load_state(_BUILT_MODULES, {})

    info = {"commit": module.get_commit_id()}
    built_modules[module.name] = info

    _save_state(_BUILT_MODULES, built_modules)

def remove_built_module(module):
    built_modules = _load_state(_BUILT_MODULES)

    if built_modules and module.name in built_modules:
        del built_modules[module.name]
        _save_state(_BUILT_MODULES, built_modules)

def check_built_module(module):
    built_modules = _load_state(_BUILT_MODULES, {})
    info = built_modules.get(module.name, {})
    return module.get_commit_id() == info.get("commit", None)

def get_last_system_check():
    system_check = _load_state(_SYSTEM_CHECK, {})
    return system_check.get("commit", None)

def touch_last_system_check():
    system_check = _load_state(_SYSTEM_CHECK, {})

    system_check["commit"] = config.get_commit_id()

    _save_state(_SYSTEM_CHECK, system_check)

def clean():
    _state = None

    print "Deleting state"

    try:
        for name in _BUILT_MODULES, _SYSTEM_CHECK:
            os.unlink(_get_state_path(name))
    except OSError:
        pass
