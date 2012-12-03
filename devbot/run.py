#!/usr/bin/python -u

import os
import string
import random
import shutil
import subprocess
import time

from devbot import environ
from devbot import config

def run(command):
    environ.setup()

    args = [command]

    resolution = config.get_pref("RESOLUTION")
    if resolution:
        args.extend(["--resolution", resolution])

    output = config.get_pref("OUTPUT")
    if output:
        args.extend(["--output", output])

    os.execlp(args[0], *args)

def run_test(command, test_path, virtual=False):
    environ.setup()

    args = [command]
    if virtual:
        args.append("--virtual")

    command_process = subprocess.Popen(args, stdout=subprocess.PIPE)
    for i in range(0, 2):
        line = command_process.stdout.readline()
        name, value = line.split("=", 1)
        os.environ[name.strip()] = value.strip()

    time.sleep(5)

    try:
        subprocess.check_call(["python", test_path])
        result = True
    except subprocess.CalledProcessError:
        result = False

    command_process.terminate()

    return result

def merge_logs(logs_path, log_name):
    logs = {}
    for filename in os.listdir(logs_path):
        if filename.endswith(".log"):
            path = os.path.join(logs_path, filename)
            with open(path) as f:
                logs[filename] = f.read()

    with open(os.path.join(config.logs_dir, log_name), "w") as f:
        for filename, log in logs.items():
            f.write("===== %s =====\n\n%s" % (filename, log))

def _get_random_id():
    return ''.join(random.choice(string.letters) for i in xrange(8))

