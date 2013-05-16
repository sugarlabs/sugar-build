from devbot import distro
from devbot.plugins import interfaces


class PackageManager(interfaces.PackageManager):
    def __init__(self, test=False, interactive=True):
        pass

    def install_packages(self, packages):
        pass

    def remove_packages(self, packages):
        pass

    def update(self):
        pass

    def find_all(self):
        return []

    def find_with_deps(self, packages):
        return []

distro.register_package_manager("unknown", PackageManager)


class DistroInfo(interfaces.DistroInfo):
    def __init__(self):
        self.lib_dir = None
        self.name = "unknown"
        self.version = "unknown"
        self.gnome_version = "3.4"
        self.valid = True
        self.supported = False

distro.register_distro_info(DistroInfo)
