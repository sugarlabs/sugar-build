SCRIPTS = $(CURDIR)/scripts
JHBUILD = $(CURDIR)/build/bin/jhbuild -f $(SCRIPTS)/jhbuildrc

submodules:
	git submodule init
	git submodule update

check-system:
	$(SCRIPTS)/check-system

install-jhbuild: submodules check-system
	cd $(SCRIPTS)/jhbuild ; \
	./autogen.sh --prefix=$(CURDIR)/build ; \
	make ; make install

build-activities: submodules
	$(JHBUILD) run $(SCRIPTS)/build-activity terminal

build-glucose: install-jhbuild check-system
	$(JHBUILD) build

build: build-glucose build-activities

build-%:
	$(JHBUILD) buildone $*

run:
	xinit $(SCRIPTS)/xinitrc -- :2

clean:
	rm -rf source
	rm -rf build
