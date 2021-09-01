import os
from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    log_level: str = 'DEBUG'
    redact_online_url: AnyUrl = 'https://api.brighter.ai/'
    redact_url_default: AnyUrl = os.getenv("REDACT_URL")
    api_key: str = os.getenv("API_KEY")
