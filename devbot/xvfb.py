import os
import subprocess

from devbot import utils


def _find_free_display():
    for i in range(100, 1000):
        display = ":%s" % i
        result = subprocess.call(args=["xdpyinfo", "--display", display],
                                 stdout=utils.devnull,
                                 stderr=subprocess.STDOUT)
        if result > 0:
            return display


def start():
    xvfb_display = _find_free_display()
    xvfb_proc = subprocess.Popen(args=["Xvfb", xvfb_display],
                                 stdout=utils.devnull,
                                 stderr=subprocess.STDOUT)
    orig_display = os.environ.get("DISPLAY", None)
    os.environ["DISPLAY"] = xvfb_display

    return (xvfb_proc, orig_display)


def stop(xvfb_proc, orig_display):
    if orig_display is not None:
        os.environ["DISPLAY"] = orig_display

    xvfb_proc.terminate()
