import os
import subprocess

from devbot import command
from devbot import distro

class PackageManager:
    def install_packages(self, packages):
        """Install packages

           :param packages: packages to install
        """

    def remove_packages(self, packages):
        """Remove a list of packages

           :param packages: packages to remove
        """

    def update(self):
        """Update packages to the latest version"""

    def find_all(self):
        """Return all the installed packages"""

    def find_with_deps(self, package_names):
        """Return all the installed dependencies of a list of packages.
           The packages itself are also returned in the list.

           :param package_names: names of the packages to find
           :returns packages with all their dependencies
        """

class DistroInfo:
    """Informations about the distribution
    """

    def __init__(self):
        self.name = None
        """Name"""

        self.version = None
        """Version"""
    
        self.system_version = None
        """Distro independent system version"""

        self.valid = False
        """If valid we running on this distribution"""

        self.use_lib64 = False
        """Install libraries in the lib64 directory"""
