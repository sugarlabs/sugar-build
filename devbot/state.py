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

def add_built_module(name, commit_id):
    _get_state()["built_modules"][name] = commit_id
    _state_changed()

def remove_built_module(name):
    del _get_state()["built_modules"][name]
    _state_changed()

def get_built_module(name):
    return _get_state()["built_modules"].get(name, None)

def clean():
    _state = None

    print "Deleting state"

    try:
        os.unlink(_get_state_path())
    except OSError:
        pass
