#!/usr/bin/python -u

import os
import string
import random
import shutil
import subprocess
import time
import tempfile

from devbot import environ
from devbot import config

def run(command):
    environ.setup()

    args = [command, "--home-dir", config.home_dir]

    resolution = config.get_pref("RESOLUTION")
    if resolution:
        args.extend(["--resolution", resolution])

    output = config.get_pref("OUTPUT")
    if output:
        args.extend(["--output", output])

    os.execlp(args[0], *args)

def run_test(command, test_path, virtual=False):
    environ.setup()

    temp_dir = tempfile.mkdtemp("sugar-build-test")
    display_path = os.path.join(temp_dir, "display")

    args = [command, "--display-path", display_path]
    if virtual:
        args.append("--virtual")

    command_process = subprocess.Popen(args, stdout=subprocess.PIPE)

    while True:
        if not os.path.exists(display_path):
            time.sleep(1)
        else:
            break

    with open(display_path) as f:
        os.environ["DISPLAY"] = f.read()

    os.unlink(display_path)
    os.rmdir(temp_dir)

    try:
        subprocess.check_call(["python", test_path])
        result = True
    except subprocess.CalledProcessError:
        result = False

    command_process.terminate()

    return result

def collect_logs(source_path, log_name):
    logs = {}
    for filename in os.listdir(source_path):
        if filename.endswith(".log"):
            path = os.path.join(source_path, filename)
            with open(path) as f:
                logs[filename] = f.read()

    log_path = config.get_log_path(log_name)
    with open(log_path, "w") as f:
        for filename, log in logs.items():
            f.write("\n===== %s =====\n\n%s" % (filename, log))

    last_log_path = os.path.join(config.logs_dir, "%s.log" % log_name)

    try:
        os.unlink(last_log_path)
    except OSError:
        pass

    os.symlink(log_path, last_log_path)

def _get_random_id():
    return ''.join(random.choice(string.letters) for i in xrange(8))

