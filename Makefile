build:
	cd redact
	flit build

install:
	make build
	pip install . --upgrade

test-installation:
	redact_file --help > /dev/null && redact_folder --help > /dev/null && echo "OK: Command-line endpoints installed"
