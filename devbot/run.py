#!/usr/bin/python -u

import os
import string
import random
import shutil
import subprocess
import time

from devbot import environ
from devbot import config

def run_sugar():
    profile_env = os.environ.get("SUGAR_PROFILE", None)
    profile_pref = config.get_pref("PROFILE")

    if profile_env is not None:
        if profile_pref is None:
            config.set_pref("PROFILE", _get_random_id()) 
        elif profile_pref == profile_env:
            print "Cannot run two instances with the same profile."
            return

    environ.setup()

    args = ["sugar-runner"]

    resolution = config.get_pref("RESOLUTION")
    if resolution:
        args.extend(["--resolution", resolution])

    output = config.get_pref("OUTPUT")
    if output:
        args.extend(["--output", output])

    os.execlp(args[0], *args)

def run_test(test_path, virtual=False):
    os.environ["SUGAR_LOGGER_LEVEL"] = "debug"
    os.environ["SUGAR_PROFILE"] = "uitests"
    os.environ["GTK_MODULES"] = "gail:atk-bridge"

    environ.setup()

    args = ["sugar-runner"]
    if virtual:
        args.append("--virtual")

    sugar_process = subprocess.Popen(args, stdout=subprocess.PIPE)
    for i in range(0, 2):
        line = sugar_process.stdout.readline()
        name, value = line.split("=", 1)
        os.environ[name.strip()] = value.strip()

    profile_path = os.path.expanduser("~/.sugar/uitests")
    shutil.rmtree(profile_path, ignore_errors=True)

    time.sleep(5)

    try:
        subprocess.check_call(["python", test_path])
        result = True
    except subprocess.CalledProcessError:
        result = False

    sugar_proces.terminate()

    logs = {}
    logs_path = os.path.join(profile_path, "logs")
    for filename in os.listdir(logs_path):
        if filename.endswith(".log"):
            path = os.path.join(logs_path, filename)
            with open(path) as f:
                logs[filename] = f.read()

    with open(os.path.join(config.logs_dir, "test.log"), "w") as f:
        for filename, log in logs.items():
            f.write("===== %s =====\n\n%s" % (filename, log))

    return result

def _get_random_id():
    return ''.join(random.choice(string.letters) for i in xrange(8))

