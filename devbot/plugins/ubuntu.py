import subprocess

from devbot import distro
from devbot.plugins import interfaces
from devbot.plugins import debian

distro.register_package_manager("ubuntu", debian.PackageManager)


class DistroInfo(interfaces.DistroInfo):
    _OS_RELEASE_PATH = "/etc/os-release"

    def __init__(self):
        arch = self._get_architecture()

        self.name = "ubuntu"
        self.version = "unknown"
        self.gnome_version = "3.4"
        self.gstreamer_version = "1.0"
        self.valid = True
        self.supported = (arch in ["i386", "i686", "x86_64"])
        self.lib_dir = None

        if arch in ["i386", "i686"]:
            self.lib_dir = "lib/i386-linux-gnu"
        elif arch == "x86_64":
            self.lib_dir = "lib/x86_64-linux-gnu"

        os_info = {}

        try:
            release = open(self._OS_RELEASE_PATH).read().strip()
            for line in release.split("\n"):
                split = line.strip().split("=")
                os_info[split[0]] = split[1].replace("\"", "")
        except IOError:
            release = None
            self.valid = False

        if os_info["ID"] != "ubuntu":
            self.valid = False

        self.version = os_info.get("VERSION_ID", None)

        if self.version != "12.10":
            self.supported = False

        if self.version and self.version >= "12.10":
            self.gnome_version = "3.6"

    def _get_architecture(self):
        return subprocess.check_output(["uname", "-i"]).strip()

distro.register_distro_info(DistroInfo)
