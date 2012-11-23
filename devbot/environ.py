from distutils import sysconfig
import os

from devbot import config

def setup():
    _setup_dirs()
    _setup_gconf()
    _setup_variables()

def _add_path(name, path):
    if name not in os.environ:
        os.environ[name] = path
        return

    splitted = os.environ[name].split(":")
    splitted.insert(0, path)

    os.environ[name] = ":".join(splitted)

def _setup_variables():
    _add_path("LD_LIBRARY_PATH", config.lib_dir)
    _add_path("PATH", config.bin_dir)
    _add_path("PATH", config.commands_dir)

    _add_path("XCURSOR_PATH",
              os.path.join(config.share_dir, "icons"))
    _add_path("GIO_EXTRA_MODULES",
              os.path.join(config.system_lib_dir, "gio", "modules"))
    _add_path("GI_TYPELIB_PATH",
              os.path.join(config.system_lib_dir, "girepository-1.0"))
    _add_path("GI_TYPELIB_PATH",
              os.path.join(config.lib_dir, "girepository-1.0"))
    _add_path("PKG_CONFIG_PATH",
              os.path.join(config.lib_dir, "pkgconfig"))
    _add_path("GST_PLUGIN_PATH",
              os.path.join(config.lib_dir , "gstreamer-1.0"))
    _add_path("GST_REGISTRY",
              os.path.join(config.devbot_dir, "gstreamer.registry"))
    _add_path("PYTHONPATH",
              sysconfig.get_python_lib(prefix=config.install_dir))
    _add_path("PYTHONPATH",
              sysconfig.get_python_lib(prefix=config.install_dir,
                                       plat_specific=True))

    _add_path("XDG_DATA_DIRS", "/usr/share")
    _add_path("XDG_DATA_DIRS", config.share_dir)

    _add_path("XDG_CONFIG_DIRS", "/etc")
    _add_path("XDG_CONFIG_DIRS", config.etc_dir)    

    os.environ["GTK_DATA_PREFIX"] = config.install_dir
    os.environ["GTK_PATH"] = os.path.join(config.lib_dir, "gtk-2.0")

def _setup_gconf():
    gconf_dir = os.path.join(config.etc_dir, "gconf")
    gconf_pathdir = os.path.join(gconf_dir, "2")

    if not os.path.exists(gconf_pathdir):
        os.makedirs(gconf_pathdir)

    gconf_path = os.path.join(gconf_pathdir, "path.jhbuild")
    if not os.path.exists(gconf_path):
        input = open("/etc/gconf/2/path")
        output = open(gconf_path, "w")

        for line in input.readlines():
            if "/etc/gconf" in line:
                output.write(line.replace("/etc/gconf", gconf_dir))
            output.write(line)

        output.close()
        input.close()

    os.environ["GCONF_DEFAULT_SOURCE_PATH"] = gconf_path

    os.environ["GCONF_SCHEMA_INSTALL_SOURCE"] = \
        "xml:merged:" + os.path.join(gconf_dir, "gconf.xml.defaults")

def _setup_dirs():
    for dir in [config.source_dir,
                config.install_dir,
                config.build_dir,
                config.share_dir,
                config.devbot_dir,
                os.path.join(config.share_dir, "aclocal")]:
        if not os.path.exists(dir):
            os.mkdir(dir)
