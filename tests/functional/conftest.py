import pytest

from ips_client.data_models import ServiceType, OutputType
from ips_client.ips_instance import IPSInstance
from ips_client.ips_requests import IPSRequests
from ips_client.job import IPSJob
from ips_client.settings import Settings


settings = Settings()


@pytest.fixture
def ips_requests(ips_url) -> IPSRequests:
    return IPSRequests(ips_url=ips_url)


@pytest.fixture(params=[ServiceType.dnat, ServiceType.blur, ServiceType.extract])
def any_img_ips(ips_url, request) -> IPSInstance:
    service = request.param
    out_type = OutputType.overlays if service == ServiceType.extract else OutputType.images
    return IPSInstance.create(service=service, out_type=out_type, ips_url=ips_url)


@pytest.fixture
def job(any_img_ips, some_image) -> IPSJob:
    return any_img_ips.start_job(file=some_image)
