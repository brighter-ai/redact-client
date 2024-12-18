import logging
import shutil
from pathlib import Path
from typing import IO, Optional

import pytest

from redact.settings import Settings

settings = Settings()

logger = logging.getLogger()

NUMBER_OF_IMAGES = 3


def pytest_addoption(parser):
    parser.addoption(
        "--redact_url",
        action="store",
        default=None,
        help="URL of a running Redact instance",
    )
    parser.addoption(
        "--api_key", action="store", default=None, help="API key for Redact Online"
    )


@pytest.fixture(scope="session")
def redact_url(request) -> str:
    url = request.config.getoption("--redact_url")
    if not url:
        url = settings.redact_url_default
        logging.warning(f"No --redact_url given. Falling back to default: {url}")
    return url


@pytest.fixture(scope="session")
def optional_api_key(request) -> Optional[str]:
    api_key = request.config.getoption("--api_key")
    return api_key or None


@pytest.fixture
def api_key(request) -> str:
    api_key = request.config.getoption("--api_key")
    if not api_key:
        raise ValueError("Test requires a valid --api_key")
    return api_key


@pytest.fixture(scope="session")
def resource_path() -> Path:
    return Path(__file__).parent / "resources"


@pytest.fixture
def some_image(resource_path: Path) -> IO[bytes]:
    img_path = resource_path / "obama.jpeg"
    with open(img_path, "rb") as f:
        yield f


@pytest.fixture
def some_custom_lp_stamp(resource_path: Path) -> IO:
    img_path = resource_path / "licence_plate_custom_stamp.png"
    with open(img_path, "rb") as f:
        yield f


@pytest.fixture
def images_path(tmp_path_factory, some_image, n_images: int = NUMBER_OF_IMAGES) -> Path:
    """
    Return a temporary directory that has been prepared with some image files:
    - img_0.jpg
    - img_1.jpg
    - img_2.jpg
    - ...
    """
    tmp_img_path = tmp_path_factory.mktemp("imgs_dir")
    for i in range(n_images):
        output_path = tmp_img_path / f"sub_dir/img_{i}.jpeg"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        some_image.seek(0)
        with open(str(output_path), "wb") as f:
            shutil.copyfileobj(fsrc=some_image, fdst=f)
    return tmp_img_path


def _copy_file_to_tmp_path(tmp_path: Path, file_path: Path):
    target_file_path = tmp_path / file_path.name
    shutil.copy(file_path, target_file_path)
    return target_file_path


@pytest.fixture
def image_path(tmp_path, resource_path):
    img_path = resource_path / "obama.jpeg"
    return _copy_file_to_tmp_path(tmp_path=tmp_path, file_path=img_path)


@pytest.fixture
def video_path(tmp_path, resource_path):
    video_path = resource_path / "not_starting_with_keyframe.mp4"
    return _copy_file_to_tmp_path(tmp_path=tmp_path, file_path=video_path)


@pytest.fixture
def broken_video_path(tmp_path, resource_path):
    video_path = resource_path / "broken_video.mp4"
    return _copy_file_to_tmp_path(tmp_path=tmp_path, file_path=video_path)
