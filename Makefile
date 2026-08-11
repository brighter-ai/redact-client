VERSION=11.0.0

SHELL := /bin/bash

.PHONY: build install test-functional test-unit test-integration test-cmd-install

build:
	uv build

install:
	uv sync --dev

reinstall:
	uv sync --dev --reinstall

uninstall:
	pip uninstall redact
	
test-functional:
	uv run pytest tests/${api_version}/functional/ --api_key $(api_key) --redact_url $(redact_url)

test-unit:
	uv run pytest tests/commons/

test-integration:
	uv run pytest tests/${api_version}/integration/

test-cmd-install:
	uv run redact_file --help && uv run redact_folder --help && echo "OK: Command-line endpoints installed"
