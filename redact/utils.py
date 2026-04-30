import re
import urllib.parse
import warnings
from typing import Dict


def normalize_url(url: str, allow_http: bool = False) -> str:
    """Return a fully-qualified URL.

    Bare hosts default to ``https://`` so the api-key header is never sent
    in cleartext. Explicit ``http://`` URLs are rejected unless
    ``allow_http`` is set; in that case a warning is emitted because the
    api-key header travels in cleartext over the wire.
    """
    parse_result = urllib.parse.urlparse(url)
    if not parse_result.scheme or not parse_result.netloc:
        scheme = "http" if allow_http else "https"
        new_url = f"{scheme}://{url}"
        if urllib.parse.urlparse(new_url).scheme != scheme:
            raise ValueError(f"Could not parse url: {url!r}")
        url = new_url

    if urllib.parse.urlparse(url).scheme == "http":
        if not allow_http:
            raise ValueError(
                f"Refusing to use plaintext HTTP url {url!r}: the api-key "
                "header would be sent in cleartext. Pass insecure=True "
                "(or --insecure on the CLI) to override."
            )
        warnings.warn(
            f"Using plaintext HTTP for {url!r}: api-key is sent in cleartext.",
            stacklevel=2,
        )
    return url


def retrieve_file_name(headers: Dict[str, str]) -> str:
    return re.findall(r"filename=(\S+)", headers["content-disposition"])[0].replace(
        '"', ""
    )
