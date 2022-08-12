from pydantic import BaseSettings, AnyUrl, HttpUrl


class Settings(BaseSettings):
    log_level: str = "INFO"
    redact_online_url: AnyUrl = HttpUrl("https://api.brighter.ai/")
    redact_url_default: AnyUrl = HttpUrl("http://127.0.0.1:8787/")
