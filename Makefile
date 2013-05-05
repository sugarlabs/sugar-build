COMMANDS_DIR=$(CURDIR)/commands
TIME=time -f "\n= Time =\n\nreal\t%e\nuser\t%U\nsys\t%S\n"

.PHONY: build

all: build

check-system:
	@$(COMMANDS_DIR)/check-system $(ARGS)

pull:
	@$(COMMANDS_DIR)/pull $(ARGS)

build:
	@$(TIME) $(COMMANDS_DIR)/build $(ARGS)

run:
	@$(COMMANDS_DIR)/run

check:
	@$(COMMANDS_DIR)/check

shell:
	@$(COMMANDS_DIR)/shell

bug-report:
	@$(COMMANDS_DIR)/bug-report

clean:
	@$(COMMANDS_DIR)/clean

build-%:
	@$(COMMANDS_DIR)/build $*

pull-%:
	@$(COMMANDS_DIR)/pull $*

check-%:
	@$(COMMANDS_DIR)/check $*
