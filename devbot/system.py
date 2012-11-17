import json
import os
import subprocess
import sys

from devbot import config
from devbot import distro
from devbot import command

devnull = open("/dev/null", "w")
xvfb_display = ":100"

libdirs = ["lib",
           "lib64",
           "lib/x86_64-linux-gnu",
           "lib/i386-linux-gnu"]

def check_binary(check):
    return subprocess.call(["which", check],
                           stdout=devnull,
                           stderr=subprocess.STDOUT)

def check_pkgconfig(check):
    return subprocess.call(["pkg-config", "--exists", check]) == 1

def check_python(check):
    return subprocess.call(["python", "-c", check],
                           stdout=devnull, stderr=subprocess.STDOUT) == 1

def check_gtkmodule(check):
    # Not sure we can do better than this, the gtkmodule stuff is private
    missing = True
    
    for libdir in libdirs:
        if os.path.exists("/usr/%s/gtk-2.0/modules/lib%s.so" % (libdir, check)):
            missing = False

    return missing

def check_include(check):
    return not os.path.exists(os.path.join("/usr/include/", check))

def check_dbus(check):
    return not os.path.exists("/usr/share/dbus-1/services/%s.service" % check)

def check_metacity_theme(check):
    return not os.path.exists("/usr/share/themes/%s/metacity-1/metacity-theme-3.xml" % check)

def check_gstreamer(check):
    missing = True
    
    for libdir in libdirs:
        if os.path.exists("/usr/%s/gstreamer-0.10/libgst%s.so" % (libdir, check)):
            missing = False

    return missing

checkers = { "binary": check_binary,
             "python": check_python,
             "pkgconfig": check_pkgconfig,
             "gtkmodule": check_gtkmodule,
             "dbus": check_dbus,
             "gstreamer": check_gstreamer,
             "metacity-theme": check_metacity_theme,
             "include": check_include }

def load_deps_json(name):
    path = os.path.join(scriptdir, "deps", "%s.json" % name)
    return json.load(open(path))

def run_checks(package_manager, checks, packages):
    distro_name = distro.get_distro_name()

    failed_checks = []
    to_install = []

    for check in checks:
        checker = checkers[check["checker"]]
        if checker(check["check"]):
            check_name = check.get("check_name", check["check"])
            if distro_name in packages[check_name]:
                package_list = packages[check_name][distro_name]
                if not isinstance(package_list, list):
                    package_list = [package_list]

                for package in package_list:
                    # Might be none, if so skip on this distro_name
                    if package and package not in to_install:
                        to_install.append(package)
            else:
                failed_checks.append(check)

    if to_install:
        package_manager.install_packages(to_install)

    if failed_checks:
        print "Failed checks\n"
    else:
        return True

    for check in failed_checks:
        print "[%s] %s" % (check["checker"], check["check"])

    return False

def start_xvfb():
    xvfb_proc = subprocess.Popen(args=["Xvfb", xvfb_display],
                                 stdout=devnull,
                                 stderr=subprocess.STDOUT)
    orig_display = os.environ.get("DISPLAY", None)
    os.environ["DISPLAY"] = xvfb_display

    return (xvfb_proc, orig_display)

def stop_xvfb(xvfb_proc, orig_display):
    if orig_display:
        os.environ["DISPLAY"] = xvfb_display
    else:
        del os.environ["DISPLAY"]

    xvfb_proc.terminate()

def warn_if_unsupported(distro_name):
    if distro_name == "unsupported":
        print "*********************************************************\n" \
              "You are running an unsupported distribution. You might be\n" \
              "able to make sugar work by installing or building \n" \
              "packages but it certainly won't work out of the box.\n" \
              "You are strongly encouraged to pick one of the supported \n" \
              "distributions listed in the README.\n" \
              "*********************************************************\n"

def remove_packages(package_manager, packages):
    distro_name = distro.get_distro_name()

    to_keep = []
    for package_info in packages.values():
        if distro_name in package_info:
            package_list = package_info[distro_name]
            if not isinstance(package_list, list):
                package_list = [package_list]

            for package in package_list:
                if package not in to_keep:
                    to_keep.append(package)

    try:
        to_keep = package_manager.find_with_deps(to_keep)
    except NotImplementedError:
        return

    all = package_manager.find_all()

    to_remove = []
    for package in all:
        if package not in to_keep:
            to_remove.append(package)

    if to_remove:
        package_manager.remove_packages(to_remove)

def check(remove=False, update=False, test=False):
    distro_name = distro.get_distro_name()
    package_manager = distro.get_package_manager(test=test)

    packages = config.load_packages()

    checks = config.load_prerequisites()
    if not run_checks(package_manager, checks, packages):
        sys.exit(1)

    xvfb_proc, orig_display = start_xvfb()

    run_checks(package_manager, config.load_checks(), packages)

    warn_if_unsupported(distro_name)

    stop_xvfb(xvfb_proc, orig_display)

    if update:
        package_manager.update()

    if remove:
	remove_packages(package_manager, packages)
