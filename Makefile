build:
	cd redact_client
	flit build

install:
	make build
	pip install . --upgrade

test-installation:
	# Test whether the command endpoints are installed
	redact_anon_file --help
	redact_anon_folder --help
