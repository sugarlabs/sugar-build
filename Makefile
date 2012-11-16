COMMANDS = $(CURDIR)/commands

include Makefile.helpers

all: build

check-system:
	@$(COMMANDS)/check-system $(ARGS)

build: check-system
	@$(COMMANDS)/build

run: helpers
	@$(COMMANDS)/run

run-command: helpers
	@$(COMMANDS)/run-command

test: helpers
	@$(COMMANDS)/test

shell: helpers
	@$(COMMANDS)/shell

bug-report:
	@$(COMMANDS)/bug-report

clean: clean-helpers
	@$(COMMANDS)/clean
