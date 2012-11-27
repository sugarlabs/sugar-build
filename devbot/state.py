import os
import json

from devbot import config

_state = None

def _get_state_path():
    return os.path.join(config.home_dir, "state.json")

def _get_state():
    global _state

    if _state is not None:
        return _state

    state_path = _get_state_path()
    if os.path.exists(state_path):
        _state = json.load(open(state_path))
    else:
        _state = { "built_modules": {} }

    return _state

def _state_changed():
    json.dump(_state, open(_get_state_path(), "w+"))

def touch_built_commit_id(module):
    _get_state()["built_modules"][module.name] = module.get_commit_id()
    _state_changed()

def remove_built_commit_id(module):
    state = _get_state()

    if module.name in state["built_modules"]:
        del state["built_modules"][module.name]
        _state_changed()

def get_built_commit_id(module):
    return _get_state()["built_modules"].get(module.name, None)

def get_last_system_check():
    return _get_state().get("last_system_check", None)

def touch_last_system_check():
    _get_state()["last_system_check"] = config.get_commit_id()
    _state_changed()

def clean():
    _state = None

    print "Deleting state"

    try:
        os.unlink(_get_state_path())
    except OSError:
        pass
