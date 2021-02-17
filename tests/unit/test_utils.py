import pytest

from redact_client.utils import normalize_url


@pytest.mark.parametrize('input_url, output_url', [
    ('192.168.11.22', 'http://192.168.11.22'),
    ('192.168.11.22:42', 'http://192.168.11.22:42'),
    ('http://192.168.11.22', 'http://192.168.11.22'),
    ('https://192.168.11.22', 'https://192.168.11.22'),
    ('foo.org/bar', 'http://foo.org/bar'),
    ('foo.org/bar/', 'http://foo.org/bar/'),
])
def test_normalize_url(input_url: str, output_url: str):
    assert normalize_url(input_url) == output_url
