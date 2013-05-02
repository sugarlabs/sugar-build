import os
import json

from devbot import config

_BUILT_MODULES = "builtmodules"
_FULL_BUILD = "fullbuild"
_SYSTEM_CHECK = "syscheck"


def built_module_touch(module):
    from devbot import sourcestamp

    built_modules = _load_state(_BUILT_MODULES, {})

    source_stamp = sourcestamp.compute(module.get_source_dir())
    built_modules[module.name] = {"source_stamp": source_stamp}

    _save_state(_BUILT_MODULES, built_modules)


def built_module_is_unchanged(module):
    from devbot import sourcestamp

    built_modules = _load_state(_BUILT_MODULES, {})
    if module.name not in built_modules:
        return False

    built_module = built_modules[module.name]
    if "source_stamp" not in built_module:
        return False

    old_source_stamp = built_module["source_stamp"]
    new_source_stamp = sourcestamp.compute(module.get_source_dir())

    return old_source_stamp == new_source_stamp


def system_check_is_unchanged():
    try:
        from devbot import sourcestamp
    except ImportError:
        return False

    system_check = _load_state(_SYSTEM_CHECK)
    if not system_check or not "config_stamp" in system_check:
        return False

    config_stamp = sourcestamp.compute(config.config_dir)

    return system_check["config_stamp"] == config_stamp


def system_check_touch():
    try:
        from devbot import sourcestamp
    except ImportError:
        return

    system_check = _load_state(_SYSTEM_CHECK, {})

    config_stamp = sourcestamp.compute(config.config_dir)
    system_check["config_stamp"] = config_stamp

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
    print("* Deleting state")

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
