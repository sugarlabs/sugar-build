#!/usr/bin/python -u

import os

from devbot import environ

def run_command(args):
    environ.setup()
    os.execlp(args[0], *args)
