MEM_REQUESTS = inc/memRequest.py
PARSER = inc/parser.py
REQUIREMENTS = requirements.txt

all: env clean

env:
	@pip install -r $(REQUIREMENTS)

parser:
	@python3 $(PARSER)

.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
