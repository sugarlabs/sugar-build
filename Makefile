SOURCE_DIR=$(CURDIR)/source
COMMANDS_DIR=$(CURDIR)/commands
HELPERS_DIR=$(COMMANDS_DIR)/helpers
TOOLS_DIR=$(CURDIR)/tools

.PHONY: all

all: check-system pull build

include Makefile.config
include Makefile.commands
include Makefile.buildbot
