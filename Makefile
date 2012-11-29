SOURCE_DIR=$(CURDIR)/source
COMMANDS_DIR=$(CURDIR)/commands
HOME_DIR=$(CURDIR)/home
TOOLS_DIR=$(CURDIR)/tools

.PHONY: all

all: check-system pull build

include Makefile.config
include Makefile.commands
include Makefile.buildbot
include Makefile.tests
