#!/usr/bin/python

import os

from devbot import config


def clean():
    print "* Deleting logs"

    try:
        for filename in os.listdir(config.logs_dir):
            os.unlink(os.path.join(config.logs_dir, filename))
    except OSError:
        pass
