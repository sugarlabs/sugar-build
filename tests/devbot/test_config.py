import os
import tempfile
import subprocess

from devbot import git
from devbot import config
from devbot import distro

import common

tests_dir = os.path.abspath(os.path.dirname(__file__))
base_dir = os.path.dirname(os.path.dirname(tests_dir))
config_dir = os.path.join(base_dir, "config")
data_dir = os.path.join(tests_dir, "data")


class TestConfig(common.DevbotTestCase):
    def setUp(self):
        self.setup_config({"config_dir": config_dir})

    def _set_distro(self, name, version):
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

            def _get_architecture(self):
                return "x86_64"

            info_class._get_architecture = _get_architecture

        for info_class in distro._supported_distros:
            info = info_class()
            if info.name == name and info.version == version:
                distro._supported_distros = [info_class]
                distro._distro_info = None
                break

        self._check_distro_info()

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

    def _check_distro_info(self):
        distro_info = distro.get_distro_info()
        self.assertTrue(distro_info.supported)
        self.assertTrue(distro_info.valid)

    def test_fedora_18_modules(self):
        self._set_distro("fedora", "18")

        self.assertEquals("fedora", distro.get_distro_info().name)
        self.assertEquals("18", distro.get_distro_info().version)
        modules = config.load_modules()
        self._assert_no_module(modules, "gtk+")
        self._assert_no_module(modules, "gnome-keyring")
        self._assert_module(modules, "sugar")
        self._assert_module(modules, "glib")

        self._unset_distro()

    def test_ubuntu_13_04_modules(self):
        self._set_distro("ubuntu", "13.04")

        modules = config.load_modules()
        self._assert_module(modules, "glib")
        self._assert_no_module(modules, "gtk+")
        self._assert_no_module(modules, "gnome-keyring")
        self._assert_module(modules, "sugar")

        self._unset_distro()

    def test_debian_wheezy_modules(self):
        self._set_distro("debian", "7.0")

        modules = config.load_modules()
        self._assert_module(modules, "gnome-keyring")
        self._assert_module(modules, "glib")
        self._assert_module(modules, "gtk+")
        self._assert_module(modules, "sugar")

        self._unset_distro()
