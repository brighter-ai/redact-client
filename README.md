# IPS Python Client

This client provides convenient access to the IPS API. Example:

```python
from ips_client.job import IPSJob, JobArguments

job_args = JobArguments(service='dnat', out_type='images')

with open('obama.jpg', 'rb') as file:
    job = IPSJob(file=file, job_args=job_args)
    
result: bytes = job.start().wait_until_finished().download_result()
```

## Development

`ips_client` can be build as Pip package with [Flit](https://flit.readthedocs.io/). This way you can **build and install it locally**:

```shel
cd ips-client
flit build
pip install .
```

Alternatively, you can **install a specific version from GitHub**:

```shell
git+ssh://git@github.com/brighter-ai/ips-client.git@v3.0.1
```

In any case, you should bump `ips_client.__init__.__version__` when updating something.

Also, you may want to tag the new version for GitHub:

```shell
git tag -a v3.0.1 -m "Release v3.0.1"
git push --tags
```
