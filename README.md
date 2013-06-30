About
=====

sugar-build is a set of scripts to build sugar from sources. Please read the [documentation](http://developer.sugarlabs.org/dev-environment.md.html).

Hacking
=======

Before submitting changes to the config please run json-format on the json
files you modified. The script is available in the shell.

If you need to make changes to osbuild, you can clone the module

    git clone git://github.com/dnarvaez/osbuild.git

Install it for your user

    python setup.py install --user

Then remove the sandbox so that it's built using the installed osbuild

    rm -rf build/out/sandbox

