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
	source tests/.test.env && python3 -m pytest tests/functional/ --api_key "64628bfc4270401d98f8d91ea0f301db"

test-unit:
	source tests/.test.env && python3 -m pytest tests/unit/

test-integration:
	source tests/.test.env && python3 -m pytest tests/integration/

test-cmd-install:
	redact_file --help && redact_folder --help && echo "OK: Command-line endpoints installed"