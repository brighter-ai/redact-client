import pytest

from io import BufferedReader


@pytest.fixture
def test_image() -> BufferedReader:
    with open('obama.jpg', 'rb') as f:
        yield f
