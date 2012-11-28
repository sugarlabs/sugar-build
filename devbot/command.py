import subprocess
import time

_logger = None

def set_logger(logger):
    global _logger
    _logger = logger

def run(args, log=None, test=False, retry=0):
    print " ".join(args)
    if test:
        return

    full_args = args[:]
    if log is not None:
        full_args.insert(0, _logger)
        full_args.append(log)

    tries = 0
    while tries < retry + 1:
        try:
            tries = tries + 1
            subprocess.check_call(full_args)
            return
        except subprocess.CalledProcessError, e:
            if tries < retry + 1:
                print "Retrying (attempt %d) in 1 minute" % tries
                time.sleep(60)
            else:
                raise e

def run_with_sudo(args, test=False, retry=0):
    args_with_sudo = ["sudo"]
    args_with_sudo.extend(args)

    run(args_with_sudo, test=test, retry=retry)
