import os
import tempfile
import unittest
import subprocess

from devbot import git
from devbot import config
from devbot import distro

tests_dir = os.path.abspath(os.path.dirname(__file__))
base_dir = os.path.dirname(os.path.dirname(tests_dir))
config_dir = os.path.join(base_dir, "config")
data_dir = os.path.join(tests_dir, "data")

class TestConfig(unittest.TestCase):
    def _set_distro(self, name, version):
        if config.config_dir is None:
            config.set_config_dir(config_dir)
            config.load_plugins()

        self._orig = distro._supported_distros
        for info_class in distro._supported_distros:
            if info_class.__module__.endswith("fedora"):
                info_class._FEDORA_RELEASE_PATH = \
                    os.path.join(data_dir, "fedora-release-%s" % version) 

            if info_class.__module__.endswith("debian"):
                info_class._DEBIAN_VERSION_PATH = \
                    os.path.join(data_dir, "debian_version-wheezy") 

            if info_class.__module__.endswith("ubuntu"):
                info_class._OS_RELEASE_PATH = \
                    os.path.join(data_dir, "os-release-ubuntu-12.10") 

        for info_class in distro._supported_distros:
            info = info_class()
            if info.name == name and info.version == version:
                distro._supported_distros = [info_class]
                distro._distro_info = None
                break

    def _unset_distro(self):
        distro._supported_distros = self._orig

    def _find_module(self, modules, name):
        for module in modules:
            if module.name == name:
                return module

        return None

    def _assert_module(self, modules, name):
        self.assertIsNotNone(self._find_module(modules, name))

    def _assert_no_module(self, modules, name):
        self.assertIsNone(self._find_module(modules, name))

    def test_fedora_17_modules(self):
        self._set_distro("fedora", "17")

        modules = config.load_modules()
        self._assert_module(modules, "glib") 
        self._assert_module(modules, "gtk+")
        self._assert_module(modules, "gstreamer")
        self._assert_module(modules, "sugar") 
 
        self._unset_distro()

    def test_fedora_18_modules(self):
        self._set_distro("fedora", "18")


        self.assertEquals("fedora", distro.get_distro_info().name)
        self.assertEquals("18", distro.get_distro_info().version)
        modules = config.load_modules()
        self._assert_module(modules, "glib") 
        self._assert_no_module(modules, "gtk+")
        self._assert_no_module(modules, "gstreamer")
        self._assert_module(modules, "sugar") 

        self._unset_distro()

    def test_ubuntu_12_10_modules(self):
        self._set_distro("ubuntu", "12.10")

        modules = config.load_modules()
        self._assert_module(modules, "glib") 
        self._assert_no_module(modules, "gtk+")
        self._assert_no_module(modules, "gstreamer")
        self._assert_module(modules, "sugar") 

        self._unset_distro()

    def test_debian_wheezy_modules(self):
        self._set_distro("debian", "wheezy")

        modules = config.load_modules()
        self._assert_module(modules, "glib") 
        self._assert_module(modules, "gtk+")
        self._assert_module(modules, "gstreamer")
        self._assert_module(modules, "sugar") 

        self._unset_distro()
