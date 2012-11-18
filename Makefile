COMMANDS = $(CURDIR)/commands

include Makefile.helpers

all: build

auto-install:
	@$(COMMANDS)/auto-install

check-system:
	@$(COMMANDS)/check-system $(ARGS)

build: check-system
	@$(COMMANDS)/build

run: helpers
	@$(COMMANDS)/run

test: helpers
	@$(COMMANDS)/test

shell: helpers
	@$(COMMANDS)/shell

bug-report:
	@$(COMMANDS)/bug-report

clean: clean-helpers
	@$(COMMANDS)/clean

upload-docs:
	rsync -r --progress ./source/sugar-docs/build/ \
		dnarvaez@shell.sugarlabs.org:~/public_html/sugar-docs/
