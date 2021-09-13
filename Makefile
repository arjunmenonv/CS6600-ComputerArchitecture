MMU = src/main.py
LIBS = inc/*.py
REQ = requirements.txt

all: env clean mmu

env: $(REQ)
	pip install -r $(REQ)

mmu: $(MMU) $(LIBS)
	python3 $(MMU)

.PHONY: clean
clean:
	find . -type f -name ‘*.pyc’ -delete
	find . -type f -name ‘*.pyo’ -delete
