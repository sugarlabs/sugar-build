SOURCE_DIR=$(CURDIR)/source
BUILD_DIR=$(CURDIR)/build
COMMANDS_DIR=$(CURDIR)/commands
HOME_DIR=$(CURDIR)/home
TOOLS_DIR=$(CURDIR)/tools
BASE_DIR=$(CURDIR)

.PHONY: all

all: pull build

include Makefile.config
include Makefile.commands
include Makefile.buildbot
include Makefile.tests
