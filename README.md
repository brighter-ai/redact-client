# IPS Python Client

This client provides convenient access to the IPS API. Example:

```python
from ips_client.job import IPSJob

with open('tests/obama.jpg', 'rb') as file:
    job = IPSJob.start_new(file=file, service='dnat', out_type='images')

result: bytes = job.wait_until_finished().download_result()
```

## Batch Anonymization

In `ips_client.tools` you can find a function for batch anonymization of a whole folder: 

```python
from ips_client.tools.anonymize_folder import anonymize_folder

anonymize_folder(in_dir='~/in_dir', 
                 out_dir='~/out_dir', 
                 input_type='images',
                 out_type='images',
                 service='dnat',
                 n_parallel_jobs=5,
                 save_labels=True)
```

The function can also be called directly from the command line. For instance:

```shell
ips_anon_folder --help
ips_anon_folder ~/input_dir ~/output_dir images images dnat --ips-url 127.0.0.1:8787
```


## Development

`ips_client` can be build as Pip package with [Flit](https://flit.readthedocs.io/). This way you can **build and install it locally**:

```shell
cd ips-client
flit build
pip install . --upgrade
```

Alternatively, you can **install a specific version from GitHub**:

```shell
git+ssh://git@github.com/brighter-ai/ips-client.git@v3.6.0
```

In any case, you should bump `ips_client.__init__.__version__` when updating something.

Also, you may want to tag the new version for GitHub:

```shell
git tag -a v3.0.1 -m "Release v3.0.1"
git push --tags
```
