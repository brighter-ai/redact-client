build:
	cd redact
	flit build

install:
	make build
	pip install . --upgrade

test-installation:
	redact_file --help && redact_folder --help && echo "OK: Command-line endpoints installed"
