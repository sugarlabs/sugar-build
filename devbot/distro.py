import os
import subprocess

_package_managers = {}

def get_use_lib64():
    return os.uname()[4] == "x86_64" and get_distro_name() != "ubuntu"

def register_package_manager(name, package_manager):
    _package_managers[name] = package_manager

def get_package_manager(test=False, interactive=True):
    name, version = _get_distro_info()
    return _package_managers[name](test=test, interactive=interactive)

def get_system_version():
    name, version = _get_distro_info()
    if (name == "ubuntu" and version == "12.10") or \
       (name == "fedora" and version == "18"):
        return "3.6"
    else:
        return "3.4"

def get_distro_name():
    name, version = _get_distro_info()
    return name

def _get_distro_info():
    distro = "unsupported"
    version = "unknown"

    # Fedora
    try:
        fedora_release = open("/etc/fedora-release").read().strip()
        if fedora_release == "Fedora release 17 (Beefy Miracle)":
            distro = "fedora"
            version = "17"
        elif fedora_release == "Fedora release 18 (Spherical Cow)":
            distro = "fedora"
            version = "18"
    except IOError:
        pass

    # Ubuntu
    try:
        distributor = subprocess.check_output(["lsb_release", "-si"]).strip()
        release = subprocess.check_output(["lsb_release", "-sr"]).strip()

        if distributor == "Ubuntu" and release == "12.10":
            distro = "ubuntu"
            version = "12.10"
    except OSError:
        pass

    arch = subprocess.check_output(["uname", "-i"]).strip()
    if arch not in ["i386", "i686", "x86_64"]:
        distro = "unsupported"
        version = "unknown" 

    return distro, version
