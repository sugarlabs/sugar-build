import subprocess
import time

from devbot import config


def run(args, test=False, interactive=False, retry=0):
    if test:
        print(" ".join(args))
        return

    log_file = None
    subprocess_args = {"args": args}

    if config.log_path and not interactive:
        log_file = open(config.log_path, "a")
        subprocess_args["stdout"] = log_file
        subprocess_args["stderr"] = subprocess.STDOUT

    tries = 0
    while tries < retry + 1:
        try:
            tries = tries + 1
            subprocess.check_call(**subprocess_args)
            break
        except subprocess.CalledProcessError as e:
            print("\nCommand failed, tail of %s\n" % config.log_path)
            if config.log_path:
                subprocess.call(["tail", config.log_path])

            if tries < retry + 1:
                print("Retrying (attempt %d) in 1 minute" % tries)
                time.sleep(60)
            else:
                raise e

    if log_file:
        log_file.close()


def run_with_sudo(args, test=False, interactive=False, retry=0):
    args_with_sudo = ["sudo"]
    args_with_sudo.extend(args)

    print(" ".join(args_with_sudo))

    run(args_with_sudo, test=test, retry=retry, interactive=interactive)
