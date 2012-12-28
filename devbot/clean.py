from devbot import build
from devbot import logs
from devbot import state


def clean():
    build.clean()
    logs.clean()
    state.clean()
