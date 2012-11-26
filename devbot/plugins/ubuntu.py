import os
import subprocess

from devbot import command
from devbot import distro
from devbot.plugins import interfaces

class PackageManager(interfaces.PackageManager):
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

distro.register_package_manager("ubuntu", PackageManager)

class DistroInfo(interfaces.DistroInfo):
    def __init__(self):
        self.name = None
        self.version = None
        self.system_version = None
        self.valid = False
        self.use_lib64 = False
       
        if arch in ["i386", "i686", "x86_64"]:
            try:
                if self._get_distributor() == "Ubuntu" and \
                   self._get_release() == "12.10":
                    self.name = "ubuntu"
                    self.version = "12.10"
                    self.system_version = "3.6"
                    self.valid = True
            except OSError:
                pass

    def _get_distributor(self):
        return subprocess.check_output(["lsb_release", "-si"]).strip()

    def _get_release(self):
        return subprocess.check_output(["lsb_release", "-sr"]).strip()
