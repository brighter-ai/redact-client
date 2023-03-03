import re
import urllib.parse
from typing import Dict


def normalize_url(url: str):
    parse_result = urllib.parse.urlparse(url)
    if not parse_result.scheme or not parse_result.netloc:
        new_url = f"http://{url}"
        if urllib.parse.urlparse(new_url).scheme != "http":
            raise ValueError()
        return new_url
    return url


def retrieve_file_name(headers: Dict[str, str]) -> str:
    return re.findall(r"filename=(\S+)", headers["content-disposition"])[0].replace(
        '"', ""
    )
