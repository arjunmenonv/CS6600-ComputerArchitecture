MEM_REQUESTS = src/memRequest.py
PARSER = inc/parser.py
REQUIREMENTS = requirements.txt
SIMULATOR = src/main.py

all: clean run

env:
	@pip install -r $(REQUIREMENTS)

parser:
	@python3 $(PARSER)

run:
	@python3 $(SIMULATOR)

.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
