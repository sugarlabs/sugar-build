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

build: build-glucose build-activities

build-%:
	$(TYPESCRIPT) "$(JHBUILD) buildone $*" $(LOGFILE)

run:
	xinit $(SCRIPTS)/xinitrc -- :2

bug-report:
	@$(SCRIPTS)/bug-report

clean:
	rm -rf source build
	rm -f logs/*.log logs/all-logs.tar.bz2
