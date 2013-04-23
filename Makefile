COMMANDS_DIR=$(CURDIR)/commands
TIME=time -f "\n= Time =\n\nreal\t%e\nuser\t%U\nsys\t%S\n"

.PHONY: build

all: build

sourcestamp_cflags=`pkg-config --cflags python-2.7`
sourcestamp_libs=`pkg-config --libs python-2.7`

build-sourcestamp:
	@gcc -shared -fPIC -o devbot/sourcestamp.so \
		$(sourcestamp_cflags) $(sourcestamp_libs) devbot/sourcestamp.c

check-system:
	@$(COMMANDS_DIR)/check-system $(ARGS)

pull:
	@$(COMMANDS_DIR)/pull $(ARGS)

build: build-sourcestamp
	@$(TIME) $(COMMANDS_DIR)/build $(ARGS)

run: build-sourcestamp
	@$(COMMANDS_DIR)/run

check: build-sourcestamp
	@$(COMMANDS_DIR)/check

shell:
	@$(COMMANDS_DIR)/shell

bug-report:
	@$(COMMANDS_DIR)/bug-report

clean:
	@$(COMMANDS_DIR)/clean

snapshot:
	@$(COMMANDS_DIR)/snapshot

build-%:
	@$(COMMANDS_DIR)/build $*

pull-%:
	@$(COMMANDS_DIR)/pull $*

check-%:
	@$(COMMANDS_DIR)/check $*
