TIMESTAMP := $(shell date +%Y%m%d-%H%M%S)
LOGFILE = $(CURDIR)/logs/build-$(TIMESTAMP).log
SCRIPTS = $(CURDIR)/scripts
DNBUILD = $(SCRIPTS)/dn-build
LOG = $(SCRIPTS)/log-command

# The buildbot shell does not handle script properly. It's unnecessary
# anyway because we can't use interactive scripts there.
ifdef SUGAR_BUILDBOT
TYPESCRIPT = $(LOG)
else
TYPESCRIPT = script -t/tmp/sugar-build-scripttimingfd -ae -c
endif

all: build install-activities

XRANDR_LIBS = $(shell pkg-config --libs xrandr x11)
X11_LIBS = $(shell pkg-config --libs x11)

scripts/list-outputs: scripts/list-outputs.c
	gcc -o scripts/list-outputs scripts/list-outputs.c $(XRANDR_LIBS)

scripts/find-free-display: scripts/find-free-display.c
	gcc -o scripts/find-free-display scripts/find-free-display.c $(X11_LIBS)

x11-utils: scripts/list-outputs scripts/find-free-display 

check-system:
	$(TYPESCRIPT) $(SCRIPTS)/check-system $(LOGFILE)

build: check-system
	$(LOG) "$(DNBUILD) build" $(LOGFILE)

run: x11-utils
	$(SCRIPTS)/shell/start-sugar

test: x11-utils
	$(LOG) "$(SCRIPTS)/run-ui-tests" $(LOGFILE)

shell: x11-utils
	@PS1="[sugar-build \W]$$ " \
	PATH=$(PATH):$(SCRIPTS)/shell \
	SUGAR_BUILD_SHELL=yes \
	$(DNBUILD) shell

bug-report:
	@$(SCRIPTS)/bug-report

clean:
	rm -rf build install
	rm -rf source/gstreamer
	rm -rf source/gst-plugins-base
	rm -rf source/gst-plugins-good
	rm -rf source/gst-plugins-espeak
	rm -rf source/gst-plugins-bad
	rm -rf source/gst-plugins-ugly
	rm -rf source/gst-ffmpeg
	rm -rf source/sugar-fructose
	rm -f logs/*.log logs/all-logs.tar.bz2
	rm -f scripts/list-outputs
	rm -f scripts/find-free-display
