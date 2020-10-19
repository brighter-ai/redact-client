import urllib.parse


def normalize_url(url: str):
    parse_result = urllib.parse.urlparse(url)
    if not parse_result.scheme:
        new_url = f'http://{url}'
        assert urllib.parse.urlparse(new_url).scheme == 'http'
        assert urllib.parse.urlparse(new_url).netloc == url, f'Error with URL: {new_url}'
        return new_url
    return url
