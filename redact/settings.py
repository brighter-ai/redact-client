from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    log_level: str = "INFO"
    redact_online_url: str = "https://api.brighter.ai/"
    redact_url_default: str = "http://127.0.0.1:8787/"
