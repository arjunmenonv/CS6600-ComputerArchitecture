MEM_REQUESTS = src/memRequest.py
PARSER = inc/parser.py
REQUIREMENTS = requirements.txt
SIMULATOR = src/main.py
PWD = $(shell pwd)

input?=input/input.txt

all: clean run

env:
	@pip install -r $(REQUIREMENTS)
	@. ./env.sh

pdf:
	$(MAKE) -C doc pdf

run:
	@python3 $(SIMULATOR) -i $(input)

.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	$(MAKE) -C doc clean
