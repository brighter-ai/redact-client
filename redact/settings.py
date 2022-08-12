from pydantic import BaseSettings, AnyUrl, Field


class Settings(BaseSettings):
    log_level: str = "INFO"
    redact_online_url: AnyUrl = Field("https://api.brighter.ai/")
    redact_url_default: AnyUrl = Field("http://127.0.0.1:8787/")
