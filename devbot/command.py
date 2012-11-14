import subprocess

def run_command(args):
    print " ".join(args)
    subprocess.check_call(args)

def run_with_sudo(args):
    args_with_sudo = ["sudo"]
    args_with_sudo.extend(args)

    run_command(args_with_sudo)
