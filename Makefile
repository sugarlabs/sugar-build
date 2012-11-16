SCRIPTS = $(CURDIR)/scripts
COMMANDS = $(CURDIR)/commands

all: build

XRANDR_LIBS = $(shell pkg-config --libs xrandr x11)
X11_LIBS = $(shell pkg-config --libs x11)

scripts/list-outputs: scripts/list-outputs.c
	gcc -o scripts/list-outputs scripts/list-outputs.c $(XRANDR_LIBS)

scripts/find-free-display: scripts/find-free-display.c
	gcc -o scripts/find-free-display scripts/find-free-display.c $(X11_LIBS)

x11-utils: scripts/list-outputs scripts/find-free-display 

check-system:
	$(COMMANDS)/check-system $(ARGS)

build: check-system
	$(COMMANDS)/build

run: x11-utils
	$(SCRIPTS)/shell/start-sugar

test: x11-utils
	$(SCRIPTS)/run-ui-tests

shell: x11-utils
	@PS1="[sugar-build \W]$$ " \
	PATH=$(PATH):$(SCRIPTS)/shell \
	SUGAR_BUILD_SHELL=yes \
	$(COMMANDS)/shell

bug-report:
	@$(SCRIPTS)/bug-report

clean:
	$(COMMANDS)/clean
	rm -f logs/*.log logs/all-logs.tar.bz2
	rm -f scripts/list-outputs
	rm -f scripts/find-free-display
