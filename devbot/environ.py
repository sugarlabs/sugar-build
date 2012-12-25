from distutils import sysconfig
import os

from devbot import config

def setup():
    _setup_gconf()
    _setup_variables()

def add_path(name, path):
    if not path.endswith("/"):
        path = "%s/" % path

    if name not in os.environ:
        os.environ[name] = path
        return

    splitted = os.environ[name].split(":")
    if path not in splitted:
        splitted.insert(0, path)

    os.environ[name] = ":".join(splitted)

def _setup_variables():
    add_path("LD_LIBRARY_PATH", config.lib_dir)
    add_path("PATH", config.bin_dir)

    add_path("XCURSOR_PATH",
             os.path.join(config.share_dir, "icons"))
    add_path("PKG_CONFIG_PATH",
             os.path.join(config.lib_dir, "pkgconfig"))
    add_path("GST_PLUGIN_PATH",
             os.path.join(config.lib_dir , "gstreamer-1.0"))
    add_path("PYTHONPATH",
             sysconfig.get_python_lib(prefix=config.prefix_dir))
    add_path("PYTHONPATH",
             sysconfig.get_python_lib(prefix=config.prefix_dir,
                                      plat_specific=True))
    add_path("PYTHONPATH",
             os.path.dirname(os.path.dirname(__file__)))

    add_path("ACLOCAL_PATH", "/usr/share/aclocal")
    add_path("ACLOCAL_FLAGS", "-I /usr/share/aclocal") 

    add_path("XDG_DATA_DIRS", "/usr/share")
    add_path("XDG_DATA_DIRS", config.share_dir)

    add_path("XDG_CONFIG_DIRS", "/etc")
    add_path("XDG_CONFIG_DIRS", config.etc_dir)    

    for system_lib_dir in config.system_lib_dirs:
        modules_path = os.path.join(system_lib_dir, "gio", "modules")
        if os.path.exists(modules_path): 
            add_path("GIO_EXTRA_MODULES", modules_path)

        typelib_path = os.path.join(system_lib_dir, "girepository-1.0")
        if os.path.exists(typelib_path):  
            add_path("GI_TYPELIB_PATH", typelib_path)

    add_path("GI_TYPELIB_PATH",
             os.path.join(config.lib_dir, "girepository-1.0"))
 
    os.environ["GTK_DATA_PREFIX"] = config.prefix_dir
    os.environ["GTK_PATH"] = os.path.join(config.lib_dir, "gtk-2.0")
    os.environ["CC"] = "ccache gcc"

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
