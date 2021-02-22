import urllib.parse


def normalize_url(url: str):
    parse_result = urllib.parse.urlparse(url)
    if not parse_result.scheme:
        new_url = f'http://{url}'
        assert urllib.parse.urlparse(new_url).scheme == 'http'
        return new_url
    return url
