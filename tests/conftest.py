import os
import pytest

from io import BufferedReader

from ips_client.job import IPSJob
from data_models import ServiceType, OutputType, JobArguments


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
def job(service, ips_url, test_image) -> IPSJob:
    return IPSJob(file=test_image,
                  service=service,
                  out_type=OutputType.images,
                  ips_url=ips_url,
                  start_job=False)
