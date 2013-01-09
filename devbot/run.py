import os
import string
import random
import subprocess
import time
import tempfile

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
    temp_dir = tempfile.mkdtemp("devbot-test-display")
    display_path = os.path.join(temp_dir, "display")

    args = [test_cmd,
            "--display-path", display_path,
            "--virtual"]

    output_fd, output_name = tempfile.mkstemp("devbot-test-output")
    output_file = os.fdopen(output_fd)

    test_cmd_process = subprocess.Popen(args,
                                        stdout=output_file,
                                        stderr=subprocess.STDOUT)

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
        command.run(["python", "-u", test_path])
        result = True
    except subprocess.CalledProcessError:
        result = False

    test_cmd_process.terminate()

    output_file.seek(0)
    with open(config.log_path, "a") as f:
        f.write(output_file.read())

    output_file.close()
    os.unlink(output_name)

    return result


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
