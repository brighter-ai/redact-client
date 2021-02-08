import pathlib
import pytest
import shutil

from pathlib import Path
from typing import IO

from ips_client.data_models import ServiceType, OutputType
from ips_client.ips_instance import IPSInstance
from ips_client.ips_requests import IPSRequests
from ips_client.job import IPSJob
from ips_client.settings import Settings


settings = Settings()


def pytest_addoption(parser):
    parser.addoption(
        '--ips_url', action='store', default=settings.ips_url_default, help='URL of a running IPS instance'
    )
    parser.addoption(
        '--subscription_key', action='store', default=None, help='Subscription key for IPS Online'
    )


@pytest.fixture(scope='session')
def ips_url(request):
    return request.config.getoption('--ips_url')


@pytest.fixture
def subscription_key(request):
    subscription_key = request.config.getoption('--subscription_key')
    if not subscription_key:
        raise ValueError("Test requires a valid --subscription_key")
    return subscription_key


@pytest.fixture
def some_image() -> IO:
    img_path = pathlib.Path(__file__).parent.joinpath('resources/obama.jpg')
    with open(img_path, 'rb') as f:
        yield f


@pytest.fixture
def ips_requests(ips_url) -> IPSRequests:
    return IPSRequests(ips_url=ips_url)


@pytest.fixture(params=[ServiceType.dnat, ServiceType.blur, ServiceType.extract])
def any_img_ips(ips_url, request) -> IPSInstance:
    service = request.param
    out_type = OutputType.overlays if service == ServiceType.extract else OutputType.images
    return IPSInstance(service=service, out_type=out_type, ips_url=ips_url)


@pytest.fixture
def job(any_img_ips, some_image) -> IPSJob:
    return any_img_ips.start_job(file=some_image)


@pytest.fixture
def images_path(tmp_path_factory, some_image, n_images: int = 3) -> Path:
    """Return a temporary directory that has been prepared with some image files (img_0.jpg, img_1.jpg, ...)."""
    tmp_img_path = tmp_path_factory.mktemp('imgs_dir')
    for i in range(n_images):
        output_path = tmp_img_path.joinpath(f'sub_dir/img_{i}.jpg')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        some_image.seek(0)
        with open(str(output_path), 'wb') as f:
            shutil.copyfileobj(fsrc=some_image, fdst=f)
    return tmp_img_path
