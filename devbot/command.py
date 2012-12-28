import subprocess
import time

from devbot import config


def run(args, test=False, retry=0):
    if test:
        print " ".join(args)
        return

    if config.log_path:
        stdout = open(config.log_path, "a")
        stderr = subprocess.STDOUT
    else:
        stdout = None
        stderr = None

    tries = 0
    while tries < retry + 1:
        try:
            tries = tries + 1
            subprocess.check_call(args, stdout=stdout, stderr=stderr)
            break
        except subprocess.CalledProcessError, e:
            print "\nCommand failed, tail of %s\n" % config.log_path
            if config.log_path:
                subprocess.call(["tail", config.log_path])

            if tries < retry + 1:
                print "Retrying (attempt %d) in 1 minute" % tries
                time.sleep(60)
            else:
                raise e

    if stdout:
        stdout.close()


def run_with_sudo(args, test=False, retry=0):
    args_with_sudo = ["sudo"]
    args_with_sudo.extend(args)

    print " ".join(args_with_sudo)

    run(args_with_sudo, test=test, retry=retry)
