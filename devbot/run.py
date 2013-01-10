import os
import string
import random
import subprocess

from devbot import config
from devbot import command


def run(cmd):
    args = [cmd, "--home-dir", config.home_dir]

    resolution = config.get_pref("RESOLUTION")
    if resolution:
        args.extend(["--resolution", resolution])

    output = config.get_pref("OUTPUT")
    if output:
        args.extend(["--output", output])

    command.run(args)


def run_test(test_cmd, test_path):
    args = [test_cmd,
            "--test-command", "python -u %s" % test_path,
            "--virtual"]

    with open(config.log_path, "a") as f:
        result = subprocess.call(args, stdout=f, stderr=subprocess.STDOUT)
        return result == 0


def collect_logs(source_path):
    logs = {}
    for filename in os.listdir(source_path):
        if filename.endswith(".log"):
            path = os.path.join(source_path, filename)
            with open(path) as f:
                logs[filename] = f.read()

    with open(config.log_path, "a") as f:
        for filename, log in logs.items():
            f.write("\n===== %s =====\n\n%s" % (filename, log))


def _get_random_id():
    return ''.join(random.choice(string.letters) for i in xrange(8))
