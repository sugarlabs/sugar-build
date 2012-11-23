#!/usr/bin/python

import os

from devbot import environ
from devbot import config

def start(rcfile):
    environ.setup()

    bash_path = "/bin/bash"
    os.execlp(bash_path, bash_path, "--rcfile", rcfile)
