import pathlib
import pytest

from typing import IO

from ips_client.data_models import ServiceType, OutputType
from ips_client.ips_async_requests import IPSAsyncRequests
from ips_client.ips_requests import IPSRequests
from ips_client.job import IPSJob
from ips_client.settings import Settings


settings = Settings()


def pytest_addoption(parser):
    parser.addoption(
        '--ips_url', action='store', default=settings.ips_url_default, help='URL of a running IPS instance'
    )


@pytest.fixture
def ips_url(request):
    return request.config.getoption('--ips_url')


@pytest.fixture
def test_image() -> IO:
    img_path = pathlib.Path(__file__).parent.joinpath('obama.jpg')
    with open(img_path, 'rb') as f:
        yield f


@pytest.fixture(params=[ServiceType.dnat, ServiceType.blur])
def service(request) -> ServiceType:
    return request.param


@pytest.fixture
def ips(ips_url) -> IPSRequests:
    return IPSRequests(ips_url=ips_url)


@pytest.fixture
def ips_async(ips_url) -> IPSAsyncRequests:
    return IPSAsyncRequests(ips_url=ips_url)


@pytest.fixture
def job(service, ips_url, test_image) -> IPSJob:
    return IPSJob(file=test_image,
                  service=service,
                  out_type=OutputType.images,
                  ips_url=ips_url,
                  start_job=False)
