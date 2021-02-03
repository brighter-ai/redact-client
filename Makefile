build:
	cd ips_client
	flit build

install:
	make build
	pip install . --upgrade

test-build:
	make build
	pip install pipenv
	pipenv install .
	pipenv shell ips_anon_file
	pipenv shell ips_anon_folder
