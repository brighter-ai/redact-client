[![Brighter AI logo](brighter.png)](https://brighter.ai/)

# Redact Python Client

[![Unit + Integration Tests](https://github.com/brighter-ai/redact-client/actions/workflows/pytest.yml/badge.svg)](https://github.com/brighter-ai/redact-client/actions/workflows/pytest.yml) [![Python Linter](https://github.com/brighter-ai/redact-client/actions/workflows/flake8.yml/badge.svg)](https://github.com/brighter-ai/redact-client/actions/workflows/flake8.yml) [![Python Package Build](https://github.com/brighter-ai/redact-client/actions/workflows/build.yml/badge.svg)](https://github.com/brighter-ai/redact-client/actions/workflows/build.yml)

- [Redact Python Client](#redact-python-client)
- [Overview](#overview)
  - [Installation](#installation)
  - [Quickstart](#quickstart)
    - [Examples](#examples)
  - [Library Usage](#library-usage)
    - [(Batch) File Processing](#batch-file-processing)
    - [API Requests](#api-requests)
    - [Redact Jobs](#redact-jobs)
    - [Advanced](#advanced)

# Overview

This repository provides access to [brighter AI's](https://brighter.ai/) [Redact API](https://docs.brighter.ai/docs/) for the anonymization of faces and license plates.

Learn more:

- About us: [Brighter AI](https://brighter.ai/)
- Try [Redact](https://brighter.ai/product/) online
- [API Documentation](https://docs.brighter.ai/docs/)

## Installation

Directly install the latest version from GitHub:

```shell
pip install git+https://github.com/brighter-ai/redact-client.git
```

For a specific version, append `@[version]`.

## Quickstart

The pip package automatically installs two command-line shortcuts (`redact_file` and `redact_folder`) that let you
anonymize individual files or whole folders, respectively. For each of these commands the desired api version have to be specified.

```shell
Usage: redact_file v4 --file-path [FILE_PATH] --output-type [OUTPUT_TYPE] --service [SERVICE]
```

```shell
Usage: redact_folder v4 --input-dir [INPUT_DIR] --output-dir [OUTPUT_DIR] --input-type [INPUT_TYPE] --output-type [OUTPUT_TYPE] --service [SERVICE]
```

Add `--help` to see additional options. 
```shell
Usage: 
    redact_file v4 --help
    redact_folder v4 --help
```
For extended logs you can use for example `--verbose-logging`.

### Examples

Anonymize an individual image from the command line:

```shell
redact_file v4 --file-path image.jpg --output-type images --service blur --redact-url=http://127.0.0.1:8787
```

Per default, the result will be stored in `image_redacted.jpg` if the OUTPUT_DIR
is the same as INPUT_DIR, and the original file name is used if OUTPUT_DIR != INPUT_DIR. There will be no new request processed if an corresponding result file already exists!

Larger amounts of data (images in this case) can be
anonymized in batches:

```shell
redact_folder v4 --input-dir ./input_dir --output-dir ./output_dir --input-type images --output-type images --service blur --redact-url=127.0.0.1:8787
```

## Library Usage

The `redact` package itself provides different ways to use the Redact API from Python.

### (Batch) File Processing

The command-line shortcuts described above can be called programmatically through modules
`redact.redact_file` and `redact.redact_folder`. The latter has the optional argument `--n-parallel-jobs` for
anonymizing several objects in parallel which can result in a significant speed-up when processing many
small files.

### API Requests

The class `redact.RedactRequests` maps the [API endpoints](https://docs.identity.ps/) to Python methods.
It is intended to reduce boiler-plate code around the API calls.
> NOTE: default API version is set to v4. If want to use version v3, please refer to the [Different API version](#Different-API-version)

### Redact Jobs

In addition, the classes `RedactInstance` and `RedactJob` provide convenient high-level access to the API:

```python
from redact import RedactInstance, ServiceType, OutputType

redact = RedactInstance.create(service=ServiceType.blur, out_type=OutputType.images, redact_url='http://127.0.0.1:8787')
with open('image.jpg', 'rb') as f:
    result = redact.start_job(file=f).wait_until_finished().download_result()
```

For using Redact Online you will need to provide a valid api_key:
```python
from redact import RedactInstance, ServiceType, OutputType

redact = RedactInstance.create(service=ServiceType.blur, out_type=OutputType.images, redact_url='https://api.brighter.ai/', api_key="VALID_API_KEY")
```

#### Different API version
In case you use a different api version than the default, you have to import the corresponding classes from the version module instead from `redact`, e.g.:

```python
from redact.v3 import RedactInstance, ServiceType, OutputType, JobLabels
```
> IMPORTANT! It is recommended to switch to API version v4, v3 will be removed in the future.   

### Advanced

The anonymization can be further configured by adding additional `JobArguments` to `start_job()`

```python
from redact import JobArguments, OutputType, RedactInstance, Region, ServiceType

redact = RedactInstance.create(
    service=ServiceType.blur,
    out_type=OutputType.images,
    redact_url="http://127.0.0.1:8787",
)
job_args = JobArguments(
    region=Region.united_states_of_america, 
    face=True, 
    license_plate=False
)
with open("tests/resources/obama.jpg", "rb") as f:
    job = redact.start_job(file=f, job_args=job_args)
result = job.wait_until_finished().download_result()
```