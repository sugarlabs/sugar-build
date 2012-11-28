import os
import subprocess

from devbot import utils

xvfb_display = ":100"

def start():
    xvfb_proc = subprocess.Popen(args=["Xvfb", xvfb_display],
                                 stdout=utils.devnull,
                                 stderr=subprocess.STDOUT)
    orig_display = os.environ.get("DISPLAY", None)
    os.environ["DISPLAY"] = xvfb_display

    return (xvfb_proc, orig_display)

def stop(xvfb_proc, orig_display):
    if orig_display:
        os.environ["DISPLAY"] = xvfb_display
    else:
        del os.environ["DISPLAY"]

    xvfb_proc.terminate()
