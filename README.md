[![Brighter AI logo](brighter.png)](https://brighter.ai/)

# IPS Python Client

This project provides convenient access to Brighter AI's [Identity Protection Suite (IPS) API](https://docs.identity.ps/) 
for the anonymization of faces and license plates.

Lear more:
- About us: [Brighter AI](https://brighter.ai/)
- Try [Identity Protection Suite](https://product.brighter.ai/) (IPS) online
- [API Documentation](https://docs.identity.ps/)

## Installation

Directly install the latest version from GitHub: 

```shell
pip install git+ssh://git@github.com/brighter-ai/ips-client.git
```

For a specific version, append `@[version]`. 


## Quickstart

The pip package automatically installs two command-line shortcuts (`ips_anon_file` and `ips_anon_folder`) that let you 
anonymize individual files or whole folders, respectively.

```shell
Usage: ips_anon_file [OPTIONS] FILE_PATH
                     OUT_TYPE:[images|videos|archives|overlays]
                     SERVICE:[blur|dnat|extract]
```

```shell
Usage: ips_anon_folder [OPTIONS] IN_DIR OUT_DIR
                       INPUT_TYPE:[images|videos|archives]
                       OUT_TYPE:[images|videos|archives|overlays]
                       SERVICE:[blur|dnat|extract]
```

Add `--help` to see additional options. 


### Examples

Anonymize an individual image from the command line:

```shell
ips_anon_file image.jpg images blur --ips-url=http://127.0.0.1:8787
```

Per default, the result will be stored in `image_anonymized.jpg`.

Larger amounts of data (images in this case) can be 
anonymized in batches:

```shell
ips_anon_folder ./in_dir ./out_dir images images blur --ips-url=127.0.0.1:8787
```


## Library Usage

The `ips_client` package itself provides different ways to use the IPS API from Python.

### (Batch) File Processing

The command-line shortcuts described above can be called programmatically through modules 
`ips_client.tools.anonymize_file` and `ips_client.tools.anonymize_folder`. The latter allows for anonymizing
several objects in parallel which usually results in a significant speed-up.

### API Requests

The class `ips_client.ips_requests.IPSRequests` maps the [API endpoints](https://docs.identity.ps/) to Python methods.  
It is intended to reduce boiler-plate code around the API calls.

### IPS Jobs

In addition, the classes `IPSInstance` and `IPSJob` provide convenient high-level access to the API: 

```python
from ips_client.ips_instance import IPSInstance

ips = IPSInstance.create(service='blur', out_type='images', ips_url='http://127.0.0.1:8787')
with open('image.jpg', 'rb') as f:
    result = ips.start_job(file=f).wait_until_finished().download_result()
```

The anonymization can be further configured by adding additional `JobArguments` to `start_job()`. See `example.py`.
