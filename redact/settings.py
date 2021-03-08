from pydantic import BaseSettings


class Settings(BaseSettings):

    log_level: str = 'INFO'

    redact_online_url: str = 'https://api.identity.ps/'
    redact_url_default: str = 'http://127.0.0.1:8787/'

    requests_timeout: int = 60
    retry_attempts: int = 10
