import os
import subprocess

from devbot import command

class FedoraPackageManager:
    def __init__(test=False):
        self._test = test

    def install_packages(self, packages):
        args = ["yum"]

        if "SUGAR_BUILDBOT" in os.environ:
            args.append("-y")

        args.append("install")
        args.extend(packages)

        command.run_with_sudo(args, test=self._test)

    def remove_packages(self, packages):
        args = ["rpm", "-e"]
        args.extend(packages)

        command.run_with_sudo(args, test=self._test)

    def update(self):
        args = ["yum"]

        if "SUGAR_BUILDBOT" in os.environ:
            args.append("-y")

        args.append("update")

        command.run_with_sudo(args, test=self._test)

    def find_all(self):
        query_format = "--queryformat=[%{NAME} ]"
        all = subprocess.check_output(["rpm", "-qa", query_format]).strip()
        return all.split(" ")

    def find_with_deps(self, packages):
        result = []

        for package in packages:
            if package not in result:
                result.append(package)

            self._find_deps(package, result)

        return result

    def _find_deps(self, package, result):
        query_format = "--queryformat=[%{REQUIRENAME} ]"

        try:
            capabilities = subprocess.check_output(["rpm", "-q",
                                                    query_format,
                                                    package]).strip()
        except subprocess.CalledProcessError:
            print "Package %s not installed" % package
            return

        for capability in capabilities.strip().split(" "):
            if capability.startswith("rpmlib"):
                continue
            query_format = "--queryformat=[%{NAME} ]"
            deps_packages = subprocess.check_output(["rpm", "-q",
                                                     query_format,
                                                     "--whatprovides",
                                                     capability]).strip()

            for dep_package in deps_packages.split(" "):
                if dep_package not in result:
                    result.append(dep_package)
                    self._find_deps(dep_package, result)

class UbuntuPackageManager:
    def __init__(test=False):
        self._test = test

    def install_packages(self, packages):
        args = ["apt-get", "install"]
        args.extend(packages)

        command.run_with_sudo(args, test=self._test)

    def remove_packages(self, packages):
        raise NotImplementedError

    def update(self):
        pass

    def find_with_deps(self, package_names):
        raise NotImplementedError

def get_package_manager(test=False):
    name, version = _get_distro_info()

    if name == "fedora":
        return FedoraPackageManager(test=test)
    elif name == "ubuntu":
        return UbuntuPackageManager(test=test)

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
