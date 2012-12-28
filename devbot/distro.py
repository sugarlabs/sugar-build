_package_managers = {}
_supported_distros = []
_distro_info = None


def register_distro_info(distro_info):
    global _supported_distros
    _supported_distros.append(distro_info)


def register_package_manager(name, package_manager):
    global _package_managers
    _package_managers[name] = package_manager


def get_package_manager(test=False, interactive=True):
    global _package_managers
    package_manager_class = _package_managers[get_distro_info().name]
    return package_manager_class(test=test, interactive=interactive)


def print_distro_info():
    info = get_distro_info()
    print "\n= Distribution information =\n"
    print "Name: %s" % info.name
    print "Version: %s" % info.version
    print "GNOME version: %s" % info.gnome_version
    print "Gstreamer version: %s" % info.gstreamer_version
    print "Lib directory: %s" % info.lib_dir
    print "Supported: %s\n" % info.supported


def get_distro_info():
    global _supported_distros
    global _distro_info

    if _distro_info is not None:
        return _distro_info

    unknown_distro = None

    for info_class in _supported_distros:
        info = info_class()
        if info.name == "unknown":
            unknown_distro = info
        elif info.valid:
            _distro_info = info

    if _distro_info is None:
        _distro_info = unknown_distro

    if not _distro_info.supported:
        print "*********************************************************\n" \
              "You are running an unsupported distribution. You might be\n" \
              "able to make sugar work by installing or building \n" \
              "packages but it certainly won't work out of the box.\n" \
              "You are strongly encouraged to pick one of the supported \n" \
              "distributions listed in the README.\n" \
              "*********************************************************\n"

    return _distro_info
