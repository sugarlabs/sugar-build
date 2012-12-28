#!/usr/bin/python

import os


def start(rcfile):
    bash_path = "/bin/bash"
    os.execlp(bash_path, bash_path, "--rcfile", rcfile)
