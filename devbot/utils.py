import os

devnull = open("/dev/null", "w")

def ensure_dir(path):
    try:
        os.mkdir(path)
    except OSError:
        pass
