#!/usr/bin/python

import os

from devbot import environ

def start():
    environ.setup()

    user_shell = os.environ.get("SHELL", "/bin/sh")
    os.execlp(user_shell, user_shell)
