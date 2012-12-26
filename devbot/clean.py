from devbot import build
from devbot import logs


def clean():
    build.clean()
    logs.clean()
