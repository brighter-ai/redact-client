import urllib.parse
from typing import IO, Optional


def normalize_url(url: str):
    parse_result = urllib.parse.urlparse(url)
    if not parse_result.scheme:
        new_url = f'http://{url}'
        assert urllib.parse.urlparse(new_url).scheme == 'http'
        return new_url
    return url


def get_io_filename(file: IO, file_name: Optional[str] = None) -> str:
    """Some IO objects (i.e., FileIO) have a name attribute, but others usually don't. Therefore this helper function
    that tries to access the name attribute. If file_name is given explicitly, that's preferred, though."""
    if not file_name:
        try:
            # For file streams opened from disk, the name is available.
            # But for other streams it is not.
            file_name = file.name
        except AttributeError:
            raise ValueError('Please specify file_name (including extension)!')
    return file_name
