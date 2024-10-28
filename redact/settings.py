from pydantic import AnyUrl, BaseSettings, Field, validator


class Settings(BaseSettings):
    log_level: str = "INFO"
    redact_online_url: AnyUrl = Field("https://api.brighter.ai/")
    redact_url_default: AnyUrl = Field("http://127.0.0.1:8787/")
    base_timeout: int = 60

    @validator("log_level")
    def log_level_must_be_upper_case(cls, value: str) -> str:
        return value.upper()
