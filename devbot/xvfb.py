import os
import subprocess

from devbot import utils

_display_provider = None

def set_display_provider(provider):
    global _display_provider
    _display_provider = provider

def start():
    xvfb_display = _display_provider.find_free_display()

    xvfb_proc = subprocess.Popen(args=["Xvfb", xvfb_display],
                                 stdout=utils.devnull,
                                 stderr=subprocess.STDOUT)
    orig_display = os.environ.get("DISPLAY", None)
    os.environ["DISPLAY"] = xvfb_display

    return (xvfb_proc, orig_display)

def stop(xvfb_proc, orig_display):
    if orig_display:
        os.environ["DISPLAY"] = orig_display
    else:
        del os.environ["DISPLAY"]

    xvfb_proc.terminate()
