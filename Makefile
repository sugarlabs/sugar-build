TIMESTAMP := $(shell date +%Y%m%d-%H%M%S)
LOGFILE = $(CURDIR)/logs/build-$(TIMESTAMP).log
SCRIPTS = $(CURDIR)/scripts
JHBUILD = $(CURDIR)/build/bin/jhbuild -f $(SCRIPTS)/jhbuildrc
LOG = $(SCRIPTS)/log-command

# The buildbot shell does not handle script properly. It's unnecessary
# anyway because we can't use interactive scripts there.
ifdef SUGAR_BUILDBOT
TYPESCRIPT = $(LOG)
else
TYPESCRIPT = script -ae -c
endif

all: build

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
	./autogen.sh --prefix=$(CURDIR)/build ; \
	make ; make install

build-activities: submodules
	$(LOG) "$(JHBUILD) run $(SCRIPTS)/build-activity terminal" $(LOGFILE)

build-glucose: install-jhbuild check-system
	$(TYPESCRIPT) "$(JHBUILD) build" $(LOGFILE)

build: build-glucose build-activities scripts/list-outputs

build-%:
	$(TYPESCRIPT) "$(JHBUILD) buildone $*" $(LOGFILE)

run:
	xinit $(SCRIPTS)/xinitrc -- :99

bug-report:
	@$(SCRIPTS)/bug-report

clean:
	rm -rf source build
	rm -f logs/*.log logs/all-logs.tar.bz2
	rm -f scripts/list-outputs
