#!/usr/bin/python

from distutils.sysconfig import parse_makefile
import os
import shutil

import common

from gi.repository import Gio
from gi.repository import GLib

from devbot import config

monitors = []

def install(module, file):
    print "Installing %s" % file.get_path()

    source_dir = module.get_source_dir()
    build_dir = module.get_build_dir()

    dir = os.path.dirname(file.get_path())
    relative_path = os.path.relpath(dir, source_dir)
    makefile_path = os.path.join(build_dir, relative_path, "Makefile")
    makefile = parse_makefile(makefile_path)

    for variable in makefile:
        if variable.endswith("_PYTHON"):
            dir_variable = "%sdir" % variable.replace("_PYTHON", "")
            install_dir = makefile[dir_variable]
            shutil.copy(file.get_path(), install_dir)

def changed_cb(monitor, file, other_file, event_flags, module):
    if event_flags == Gio.FileMonitorEvent.CHANGED:
        if file.get_path().endswith(".py"):
            install(module, file)

def observe():
    for module in config.load_modules():
        if module.auto_install:
            print "Observing the %s module" % module.name

            source_dir = module.get_source_dir()
            for root, dirs, files in os.walk(source_dir):
                for dir in dirs:
                    file = Gio.File.new_for_path(os.path.join(root, dir))
                    monitor = file.monitor(Gio.FileMonitorFlags.NONE, None)
                    monitor.connect("changed", changed_cb, module)

                monitors.append(monitor)


    main_loop = GLib.MainLoop()
    main_loop.run()
