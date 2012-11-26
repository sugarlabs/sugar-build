import os
import subprocess

devnull = open("/dev/null", "w")

def get_commit_id(dir):
    orig_cwd = os.getcwd()
    os.chdir(dir)

    try:
        commit_id = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                            stderr=devnull).strip()
    except subprocess.CalledProcessError:
        commit_id = None

    os.chdir(orig_cwd)

    return commit_id
