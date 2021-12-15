import logging
import pytest
import shutil

from pathlib import Path
from typing import IO

from redact.settings import Settings


settings = Settings()

logger = logging.getLogger()


def pytest_addoption(parser):
    parser.addoption(
        '--redact_url', action='store', default=None, help='URL of a running Redact instance'
    )
    parser.addoption(
        '--api_key', action='store', default=None, help='API key for Redact Online'
    )


@pytest.fixture(scope='session')
def redact_url(request) -> str:
    url = request.config.getoption('--redact_url')
    if not url:
        url = settings.redact_url_default
        logging.warning(f'No --redact_url given. Falling back to default: {url}')
    return url


@pytest.fixture
def api_key(request) -> str:
    api_key = request.config.getoption('--api_key')
    if not api_key:
        raise ValueError("Test requires a valid --api_key")
    return api_key


@pytest.fixture(scope='session')
def resource_path() -> Path:
    return Path(__file__).parent.joinpath('resources')


@pytest.fixture
def some_image(resource_path: Path) -> IO[bytes]:
    img_path = resource_path.joinpath('obama.jpg')
    with open(img_path, 'rb') as f:
        yield f


@pytest.fixture
def some_custom_lp_stamp(resource_path: Path) -> IO:
    img_path = resource_path.joinpath('licence_plate_custom_stamp.png')
    with open(img_path, 'rb') as f:
        yield f


@pytest.fixture
def images_path(tmp_path_factory, some_image, n_images: int = 3) -> Path:
    """
    Return a temporary directory that has been prepared with some image files:
    - img_0.jpg,
    - img_1.jpg,
    - ...
    """
    tmp_img_path = tmp_path_factory.mktemp('imgs_dir')
    for i in range(n_images):
        output_path = tmp_img_path.joinpath(f'sub_dir/img_{i}.jpg')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        some_image.seek(0)
        with open(str(output_path), 'wb') as f:
            shutil.copyfileobj(fsrc=some_image, fdst=f)
    return tmp_img_path
