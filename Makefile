MMU = src/main.py
LIBS = inc/*.py
REQ = requirements.txt

env: $(REQ)
	pip install -r $(REQ)

.PHONY: clean
clean:
	find . -type f -name ‘*.pyc’ -delete
	find . -type f -name ‘*.pyo’ -delete
