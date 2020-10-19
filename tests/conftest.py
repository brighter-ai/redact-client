import os
import pytest

from io import BufferedReader

from ips_job import IPSJob, JobArguments


@pytest.fixture
def ips_url():
    return os.environ['IPS_URL']


@pytest.fixture
def test_image() -> BufferedReader:
    with open('obama.jpg', 'rb') as f:
        yield f


@pytest.fixture
def job(ips_url, test_image) -> IPSJob:
    job_args = JobArguments(service='dnat', out_type='images')
    return IPSJob(file=test_image, job_args=job_args, ips_url=ips_url, start_job=False)
