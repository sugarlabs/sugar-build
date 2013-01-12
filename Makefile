COMMANDS_DIR=$(CURDIR)/commands
TOOLS_DIR=$(CURDIR)/tools
TIME=time -f "\n= Time =\n\nreal\t%e\nuser\t%U\nsys\t%S\n"

.PHONY: all

all: build

include Makefile.config
include Makefile.commands
