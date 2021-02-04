from pydantic import BaseSettings


class Settings(BaseSettings):
    log_level: str = 'INFO'
    ips_online_url: str = 'https://api.identity.ps/'
    ips_url_default: str = 'http://127.0.0.1:8787/'
    requests_timeout: int = 30
    requests_timeout_files: int = 900  # for posting/downloading large files
