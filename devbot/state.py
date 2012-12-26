import hashlib
import os
import json

from devbot import config
from devbot import git

_BUILT_MODULES = "builtmodules"
_FULL_BUILD = "fullbuild"
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


def _get_diff_hash(git_module):
    diff = git_module.diff().strip()
    if diff:
        return hashlib.sha256(diff).hexdigest()
    else:
        return None


def _get_root_commit_id():
    git_module = git.get_root_module()
    if git_module:
        commit_id = git_module.get_commit_id()
    else:
        commit_id = "snapshot"

    return commit_id


def built_module_touch(module):
    git_module = module.get_git_module()
    built_modules = _load_state(_BUILT_MODULES, {})

    info = {"commit": git_module.get_commit_id(),
            "diff_hash": _get_diff_hash(git_module)}
    built_modules[module.name] = info

    _save_state(_BUILT_MODULES, built_modules)


def built_module_is_unchanged(module):
    git_module = module.get_git_module()
    built_modules = _load_state(_BUILT_MODULES, {})
    if module.name not in built_modules:
        return False

    info = built_modules[module.name]

    return info["diff_hash"] == _get_diff_hash(git_module) and \
           info["commit"] == git_module.get_commit_id()


def system_check_is_unchanged():
    system_check = _load_state(_SYSTEM_CHECK)
    if not system_check:
        return False

    return system_check["commit"] == _get_root_commit_id()


def system_check_touch():
    system_check = _load_state(_SYSTEM_CHECK, {})
    system_check["commit"] = _get_root_commit_id()
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

    try:
        for name in names:
            os.unlink(_get_state_path(name))
    except OSError:
        pass
