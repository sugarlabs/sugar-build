from devbot import build
from devbot import logs
from devbot import state


def clean(build_only=False):
    print("\n= Clean =\n")

    build.clean()
    state.clean(build_only=build_only)

    if not build_only:
        logs.clean()
