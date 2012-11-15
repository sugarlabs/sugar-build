import subprocess

def run(args, test=False):
    print " ".join(args)
    if not test:
        subprocess.check_call(args)

def run_with_sudo(args, test=False):
    args_with_sudo = ["sudo"]
    args_with_sudo.extend(args)

    run(args_with_sudo, test=test)
