TIMESTAMP := $(shell date +%Y%m%d-%H%M%S)
LOGFILE = $(CURDIR)/logs/build-$(TIMESTAMP).log
SCRIPTS = $(CURDIR)/scripts
JHBUILD = $(CURDIR)/install/bin/jhbuild -f $(SCRIPTS)/jhbuildrc
LOG = $(SCRIPTS)/log-command
XINITDISPLAY = `$(SCRIPTS)/find-free-display`

# The buildbot shell does not handle script properly. It's unnecessary
# anyway because we can't use interactive scripts there.
ifdef SUGAR_BUILDBOT
TYPESCRIPT = $(LOG)
else
TYPESCRIPT = script -ae -c
endif

all: build install-activities

submodules:
	git submodule init
	git submodule update

XRANDR_LIBS = $(shell pkg-config --libs xrandr x11)
X11_LIBS = $(shell pkg-config --libs x11)

scripts/list-outputs: scripts/list-outputs.c
	gcc -o scripts/list-outputs scripts/list-outputs.c $(XRANDR_LIBS)

scripts/find-free-display: scripts/find-free-display.c
	gcc -o scripts/find-free-display scripts/find-free-display.c $(X11_LIBS)

x11-utils: scripts/list-outputs scripts/find-free-display 

check-system:
	$(TYPESCRIPT) $(SCRIPTS)/check-system $(LOGFILE)

install-jhbuild: submodules check-system
	cd $(SCRIPTS)/jhbuild ; \
	./autogen.sh --prefix=$(CURDIR)/install ; \
	make ; make install

build-glucose: install-jhbuild check-system
	$(TYPESCRIPT) "$(JHBUILD) build" $(LOGFILE)

build-fructose:
	$(TYPESCRIPT) "$(JHBUILD) build -f sugar-fructose" $(LOGFILE)

build: build-glucose build-fructose 

build-%:
	$(TYPESCRIPT) "$(JHBUILD) buildone $*" $(LOGFILE)

run: x11-utils
	xinit $(SCRIPTS)/xinitrc -- $(XINITDISPLAY) &>>$(LOGFILE)

test: x11-utils
	$(LOG) "$(SCRIPTS)/run-dogtail-tests" $(LOGFILE)

shell: x11-utils
	@cd source; \
	PS1="[sugar-build \W]$$ " \
	PATH=$(PATH):$(SCRIPTS)/shell \
	SUGAR_BUILD_SHELL=yes \
	$(JHBUILD) shell

bug-report:
	@$(SCRIPTS)/bug-report

clean:
	rm -rf build install
	rm -rf source/sugar
	rm -rf source/sugar-datastore
	rm -rf source/sugar-artwork
	rm -rf source/sugar-toolkit
	rm -rf source/sugar-base
	rm -rf source/sugar-toolkit-gtk3
	rm -rf source/sugar-fructose
	rm -rf source/at-spi2-core
	rm -rf source/at-spi2-atk
	rm -rf source/gstreamer
	rm -rf source/gst-plugins-base
	rm -rf source/gst-plugins-good
	rm -f logs/*.log logs/all-logs.tar.bz2
	rm -f scripts/list-outputs
	rm -f scripts/find-free-display
