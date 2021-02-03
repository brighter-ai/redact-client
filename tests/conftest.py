import pathlib
import pytest
import shutil

from pathlib import Path
from typing import IO

from ips_client.data_models import ServiceType, OutputType
from ips_client.ips_instance import IPSInstance
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
def ips(ips_url) -> IPSInstance:
    return IPSInstance(ips_url=ips_url)


@pytest.fixture
def job(service, ips_url, test_image) -> IPSJob:
    return IPSJob.start_new(file=test_image,
                            service=service,
                            out_type=OutputType.images,
                            ips_url=ips_url)


@pytest.fixture
def images_path(tmp_path_factory, test_image, n_images: int = 3) -> Path:
    """Return a temporary directory that has been prepared with some image files (img_0.jpg, img_1.jpg, ...)."""
    tmp_img_path = tmp_path_factory.mktemp('imgs_dir')
    for i in range(n_images):
        output_path = tmp_img_path.joinpath(f'sub_dir/img_{i}.jpg')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        test_image.seek(0)
        with open(str(output_path), 'wb') as f:
            shutil.copyfileobj(fsrc=test_image, fdst=f)
    return tmp_img_path
