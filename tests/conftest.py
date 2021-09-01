import pathlib
import shutil
from pathlib import Path
from typing import IO

import pytest

from redact.settings import Settings

settings = Settings()


def pytest_addoption(parser):
    parser.addoption(
        '--redact_url', action='store', default=settings.redact_url_default, help='URL of a running Redact instance'
    )
    parser.addoption(
        '--api_key', action='store', default=None, help='API key for Redact Online'
    )


@pytest.fixture(scope='session')
def redact_url(request):
    return request.config.getoption('--redact_url')


@pytest.fixture
def api_key(request):
    api_key = request.config.getoption('--api_key')
    if not api_key:
        raise ValueError("Test requires a valid --api_key")
    return api_key


@pytest.fixture
def some_image() -> IO[bytes]:
    img_path = pathlib.Path(__file__).parent.joinpath('resources/obama.jpg')
    with open(img_path, 'rb') as f:
        yield f


@pytest.fixture
def some_custom_lp_stamp() -> IO:
    img_path = pathlib.Path(__file__).parent.joinpath('resources/licence_plate_custom_stamp.png')
    with open(img_path, 'rb') as f:
        yield f


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
