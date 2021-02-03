build:
	cd ips_client
	flit build

install:
	make build
	pip install . --upgrade

test-installation:
	ips_anon_file --help
	ips_anon_folder --help
