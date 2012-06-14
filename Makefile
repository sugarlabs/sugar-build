TIMESTAMP := $(shell date +%Y%m%d-%H%M%S)
LOGFILE = $(CURDIR)/logs/build-$(TIMESTAMP).log
SCRIPTS = $(CURDIR)/scripts
JHBUILD = $(CURDIR)/build/bin/jhbuild -f $(SCRIPTS)/jhbuildrc

submodules:
	git submodule init
	git submodule update

check-system:
	script -ae -c "$(SCRIPTS)/check-system" $(LOGFILE)

install-jhbuild: submodules check-system
	cd $(SCRIPTS)/jhbuild ; \
	./autogen.sh --prefix=$(CURDIR)/build ; \
	make ; make install

build-activities: submodules
	$(JHBUILD) run $(SCRIPTS)/build-activity terminal | tee -a $(LOGFILE)

build-glucose: install-jhbuild check-system
	script -ae -c "$(JHBUILD) build" $(LOGFILE)

build: build-glucose build-activities

build-%:
	script -ae -c "$(JHBUILD) buildone $*" $(LOGFILE)

run:
	xinit $(SCRIPTS)/xinitrc -- :2

bug-report:
	@$(SCRIPTS)/bug-report

clean:
	rm -rf source build
	rm -f logs/*.log logs/all-logs.tar.bz2
