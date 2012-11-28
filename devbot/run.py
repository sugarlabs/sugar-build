#!/usr/bin/python -u

import os
import string
import random

from devbot import environ
from devbot import config

def run(args):
    environ.setup()
    os.execlp(args[0], *args)

def run_sugar():
    profile_env = os.environ.get("SUGAR_PROFILE", None)
    profile_pref = config.get_pref("PROFILE")

    if profile_env is not None:
        if profile_pref is None:
            config.set_pref("PROFILE", _get_random_id()) 
        elif profile_pref == profile_env:
            print "Cannot run two instances with the same profile."
            return

    run(["sugar-runner"])

def _get_random_id():
    return ''.join(random.choice(string.letters) for i in xrange(8))

