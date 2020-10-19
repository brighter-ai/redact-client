import os
import pytest

from io import BufferedReader

from ips_job import IPSJob, JobArguments, ServiceType, OutputType


@pytest.fixture
def ips_url():
    return os.environ['IPS_URL']


@pytest.fixture
def test_image() -> BufferedReader:
    with open('obama.jpg', 'rb') as f:
        yield f


@pytest.fixture(params=[ServiceType.dnat, ServiceType.blur])
def service(request) -> ServiceType:
    return request.param


@pytest.fixture
def job_args(service) -> JobArguments:
    return JobArguments(service=service, out_type=OutputType.images)


@pytest.fixture
def job(job_args, ips_url, test_image) -> IPSJob:
    return IPSJob(file=test_image, job_args=job_args, ips_url=ips_url, start_job=False)
