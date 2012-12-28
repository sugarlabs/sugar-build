SOURCE_DIR=$(CURDIR)/source
BUILD_DIR=$(CURDIR)/build
COMMANDS_DIR=$(CURDIR)/commands
TESTS_DIR=$(CURDIR)/tests
TOOLS_DIR=$(CURDIR)/tools
BASE_DIR=$(CURDIR)
TIME=time -f "\n= Time =\n\nreal\t%e\nuser\t%U\nsys\t%S\n"

.PHONY: all

all: build

include Makefile.config
include Makefile.commands
include Makefile.snapshot
include Makefile.docs
