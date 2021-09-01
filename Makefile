VERSION=v4.3.0

SHELL := /bin/bash

.PHONY: build install test-functional test-unit test-integration test-cmd-install

build:
	cd redact
	flit build

install:
	make build
	pip install . --upgrade

test-functional:
	python3 -m pytest tests/functional/ --api_key 64628bfc4270401d98f8d91ea0f301db --redact_url http://192.168.77.10:14121/

test-unit:
	python3 -m pytest tests/unit/

test-integration:
	python3 -m pytest tests/integration/

test-cmd-install:
	redact_file --help && redact_folder --help && echo "OK: Command-line endpoints installed"