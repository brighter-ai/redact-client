import urllib.parse


def normalize_url(url: str):
    parse_result = urllib.parse.urlparse(url)
    if not parse_result.scheme or not parse_result.netloc:
        new_url = f'http://{url}'
        if urllib.parse.urlparse(new_url).scheme != 'http':
            raise ValueError()
        return new_url
    return url
