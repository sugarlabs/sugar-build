import os
import subprocess

from devbot import command

class FedoraPackageManager:
    def __init__(self, test=False, interactive=True):
        self._test = test
        self._interactive = interactive

    def install_packages(self, packages):
        args = ["yum"]

        if not self._interactive:
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

        if not self._interactive:
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

        filtered = [cap for cap in capabilities.split(" ")
                    if not cap.startswith("rpmlib")]

        if capabilities and filtered:
            args = ["rpm", "-q",
                    "--queryformat=[%{NAME} ]",
                    "--whatprovides"]
            args.extend(filtered)
            
            deps_packages = subprocess.check_output(args).strip()
            for dep_package in deps_packages.split(" "):
                if dep_package not in result:
                    result.append(dep_package)
                    self._find_deps(dep_package, result)

class UbuntuPackageManager:
    def __init__(self, test=False, interactive=True):
        import apt

        self._test = test
        self._interactive = interactive

        self._cache = apt.cache.Cache()

    def install_packages(self, packages):
        args = ["apt-get"]

        if not self._interactive:
            args.append("-y")

        args.append("install")
        args.extend(packages)

        command.run_with_sudo(args, test=self._test)

    def remove_packages(self, packages):
        args = ["dpkg", "-P"]
        args.extend(packages)

        command.run_with_sudo(args, test=self._test)

    def update(self):
        command.run_with_sudo(["apt-get", "update"], test=self._test)

        args = ["apt-get"]

        if not self._interactive:
            args.append("-y")

        args.append("upgrade")

        command.run_with_sudo(args, test=self._test)

    def find_all(self):
        return [package.name for package in self._cache
                if package.installed is not None]

    def _find_deps(self, package, result):
        if self._cache.is_virtual_package(package):
            for providing in self._cache.get_providing_packages(package):
                self._find_deps(providing.name, result)
            return

        if package not in self._cache:
            print "Package %s not in cache" % package
            return

        installed = self._cache[package].installed
        if installed is None:
            print "Package %s not installed" % package
            return

        for dependency in installed.dependencies:
            for base_dependency in dependency.or_dependencies:
                dependency_name = base_dependency.name
                if dependency_name not in result:
                    result.append(dependency_name)
                    self._find_deps(dependency_name, result)

    def find_with_deps(self, package_names):
        result =  []

        for package in package_names:
            if package is not None:
                self._find_deps(package, result)
                if package not in result:
                    result.append(package)

        return result

def get_use_lib64():
    return os.uname()[4] == "x86_64" and get_distro_name() != "ubuntu"

def get_package_manager(test=False, interactive=True):
    name, version = _get_distro_info()

    if name == "fedora":
        return FedoraPackageManager(test=test, interactive=interactive)
    elif name == "ubuntu":
        return UbuntuPackageManager(test=test, interactive=interactive)

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
