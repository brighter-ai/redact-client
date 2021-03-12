from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    log_level: str = 'INFO'
    redact_online_url: AnyUrl = 'https://api.identity.ps/'
    redact_url_default: AnyUrl = 'http://127.0.0.1:8787/'
