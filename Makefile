TIMESTAMP := $(shell date +%Y%m%d-%H%M%S)
LOGFILE = $(CURDIR)/logs/build-$(TIMESTAMP).log
SCRIPTS = $(CURDIR)/scripts
JHBUILD = $(CURDIR)/install/bin/jhbuild -f $(SCRIPTS)/jhbuildrc
LOG = $(SCRIPTS)/log-command

ifdef SUGAR_SESSION
XINITDISPLAY = :100
else
XINITDISPLAY = :99
endif

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

scripts/list-outputs:
	gcc -o scripts/list-outputs scripts/list-outputs.c $(XRANDR_LIBS)

check-system:
	$(TYPESCRIPT) $(SCRIPTS)/check-system $(LOGFILE)

install-jhbuild: submodules check-system
	cd $(SCRIPTS)/jhbuild ; \
	./autogen.sh --prefix=$(CURDIR)/install ; \
	make ; make install

build-glucose: install-jhbuild check-system
	$(TYPESCRIPT) "$(JHBUILD) build" $(LOGFILE)

build-fructose:
	$(TYPESCRIPT) "$(JHBUILD) build sugar-fructose" $(LOGFILE)

build: build-glucose build-fructose 

build-%:
	$(TYPESCRIPT) "$(JHBUILD) buildone $*" $(LOGFILE)

run: scripts/list-outputs
	xinit $(SCRIPTS)/xinitrc -- $(XINITDISPLAY) &>>$(LOGFILE)

test: scripts/list-outputs
	$(LOG) "$(SCRIPTS)/run-dogtail-tests" $(LOGFILE)

shell:
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
	rm -f logs/*.log logs/all-logs.tar.bz2
	rm -f scripts/list-outputs
