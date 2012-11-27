import os
import subprocess

_package_managers = {}
_distros_info = []

def register_distro_info(distro_info):
     global _distros_info
     _distros_info.append(distro_info)

def register_package_manager(name, package_manager):
    global _package_managers
    _package_managers[name] = package_manager

def get_package_manager(test=False, interactive=True):
    global _package_managers
    package_manager_class = _package_managers[get_distro_info().name]
    return package_manager_class(test=test, interactive=interactive)

def get_distro_info():
    global _distros_info

    unknown_distro = None

    for info_class in _distros_info:
        info = info_class()
        if info.name == "unknown":
            unknown_distro = info
        elif info.valid:
            return info

    return unknown_distro
