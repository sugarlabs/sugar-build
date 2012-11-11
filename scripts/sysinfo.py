import subprocess

def get_distro_name():
    distro = "unsupported"

    # Fedora
    try:
        fedora_release = open("/etc/fedora-release").read().strip()
        if fedora_release == "Fedora release 17 (Beefy Miracle)":
            distro = "fedora"
    except IOError:
        pass

    # Ubuntu
    try:
        distributor = subprocess.check_output(["lsb_release", "-si"]).strip()
        release = subprocess.check_output(["lsb_release", "-sr"]).strip()

        if distributor == "Ubuntu" and release == "12.04":
            distro = "ubuntu"
    except OSError:
        pass

    arch = subprocess.check_output(["uname", "-i"]).strip()
    if arch not in ["i386", "i686", "x86_64"]:
        distro = "unsupported" 

    return distro
