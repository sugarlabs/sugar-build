import os
import subprocess

from gi.repository import SugarRunner

from devbot import utils

def start():
    xvfb_display = SugarRunner.find_free_display()
    xvfb_proc = subprocess.Popen(args=["Xvfb", xvfb_display],
                                 stdout=utils.devnull,
                                 stderr=subprocess.STDOUT)
    orig_display = os.environ.get("DISPLAY", None)
    os.environ["DISPLAY"] = xvfb_display

    return (xvfb_proc, orig_display)

def stop(xvfb_proc, orig_display):
    os.environ["DISPLAY"] = orig_display
    xvfb_proc.terminate()
