from pydantic import BaseSettings


class Settings(BaseSettings):
    log_level: str = 'DEBUG'
    ips_url_default: str = 'http://127.0.0.1:8787/'
    requests_timeout: int = 15
