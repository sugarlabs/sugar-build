COMMANDS = $(CURDIR)/commands

all: build

XRANDR_LIBS = $(shell pkg-config --libs xrandr x11)
X11_LIBS = $(shell pkg-config --libs x11)

commands/helpers/list-outputs: commands/helpers/list-outputs.c
	gcc -o commands/helpers/list-outputs \
            commands/helpers/list-outputs.c $(XRANDR_LIBS)

commands/helpers/find-free-display: commands/helpers/find-free-display.c
	gcc -o commands/helpers/find-free-display \
            commands/helpers/find-free-display.c $(X11_LIBS)

x11-utils: commands/helpers/list-outputs commands/helpers/find-free-display 

check-system:
	$(COMMANDS)/check-system $(ARGS)

build: check-system
	$(COMMANDS)/build

run: x11-utils
	$(COMMANDS)/run

run-command: x11-utils
	$(COMMANDS)/run-command

test: x11-utils
	$(COMMANDS)/test

shell: x11-utils
	@PS1="[sugar-build \W]$$ " \
	$(COMMANDS)/shell

bug-report:
	$(COMMANDS)/bug-report

clean:
	$(COMMANDS)/clean
	rm -f logs/*.log logs/all-logs.tar.bz2
	rm -f scripts/list-outputs
	rm -f scripts/find-free-display
