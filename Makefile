VERSION=v4.3.0

SHELL := /bin/bash

.PHONY: build install test-functional

build:
	cd redact
	flit build

install:
	make build
	pip install . --upgrade

test-functional:
	source tests/.test.env && python3 -m pytest tests/functional/

test-unit:
	source tests/.test.env && python3 -m pytest tests/unit/

test-integration:
	source tests/.test.env && python3 -m pytest tests/integration/
