VERSION=10.0.0

SHELL := /bin/bash

.PHONY: build install test-functional test-unit test-integration test-cmd-install

build:
	poetry build

install:
	make build
	pip install . --upgrade

reinstall:
	make build
	pip install . --force-reinstall --upgrade

uninstall:
	pip uninstall redact
	
test-functional:
	poetry run pytest tests/${api_version}/functional/ --api_key $(api_key) --redact_url $(redact_url)

test-unit:
	poetry run pytest tests/commons/

test-integration:
	poetry run pytest tests/${api_version}/integration/

test-cmd-install:
	redact_file --help && redact_folder --help && echo "OK: Command-line endpoints installed"
