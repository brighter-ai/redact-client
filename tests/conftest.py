import pytest

from io import FileIO


@pytest.fixture
def test_image():
    with open('obama.jpg', 'rb') as f:
        yield f
