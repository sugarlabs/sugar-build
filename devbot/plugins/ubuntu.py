import subprocess

from devbot import distro
from devbot.plugins import interfaces
from devbot.plugins import debian

distro.register_package_manager("ubuntu", debian.PackageManager)

class DistroInfo(interfaces.DistroInfo):
    def __init__(self):
        arch = subprocess.check_output(["uname", "-i"]).strip() 
 
        self.name = "ubuntu"
        self.version = "unknown"
        self.gnome_version = "3.4"
        self.gstreamer_version = "1.0"
        self.valid = True
        self.supported = (arch in ["i386", "i686", "x86_64"])
        self.use_lib64 = False
 
        if self._get_distributor() != "Ubuntu":
            self.valid = False
       
        self.version = self._get_release()

        if self.version != "12.10":
            self.supported = False

        if self.version and self.version >= "12.10":
            self.gnome_version = "3.6"

    def _get_distributor(self):
        try:
            return subprocess.check_output(["lsb_release", "-si"]).strip()
        except OSError:
            None

    def _get_release(self):
        try:
            return subprocess.check_output(["lsb_release", "-sr"]).strip()
        except OSError:
            return None

distro.register_distro_info(DistroInfo)
