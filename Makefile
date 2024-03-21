# Makefile

VENV_NAME := venv
VENV_DIR := $(CURDIR)/$(VENV_NAME)
REQUIREMENTS_FILE := requirements.txt

.PHONY: init-venv install-requirements clean-venv freeze

freeze:
	pip freeze > requirements.txt

init-venv:
	python3 -m venv $(VENV_NAME)

install-requirements: init-venv
	$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS_FILE)

run:
	$(VENV_DIR)/bin/python3 main.py

clean-venv:
	rm -rf $(VENV_NAME)

# Example usage: make init-venv
#                make install-requirements
#                make clean-venv
