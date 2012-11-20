import subprocess
import time

def run(args, test=False, retry=0):
    print " ".join(args)
    if test:
        return

    tries = 0
    while tries < retry + 1:
        try:
            tries = tries + 1
            subprocess.check_call(args)
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
