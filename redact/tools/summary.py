import functools
import time
from logging import Logger
from typing import Any, Callable

from pydantic import BaseModel


class JobsSummary(BaseModel):
    failed: int = 0
    warnings: int = 0
    successful: int = 0


class TimeSummary(BaseModel):
    time_overall: float
    seconds: str
    minutes: str
    hours: str


RedactFolder = RedactFolderWrapper = Callable[..., JobsSummary]


def summary(logger: Logger) -> Callable[[RedactFolder], RedactFolderWrapper]:
    def decorator(redact_folder: RedactFolder) -> RedactFolderWrapper:
        @functools.wraps(redact_folder)
        def wrapper(*args: Any, **kwargs: Any) -> JobsSummary:
            start_time = time.time()

            jobs_summary = redact_folder(*args, **kwargs)

            end_time = time.time()
            time_difference = round(end_time - start_time, 1)

            time_summary = calculate_time_summary(time_difference)

            log_summary(logger, jobs_summary, time_summary)

            return jobs_summary

        return wrapper

    return decorator


def calculate_time_summary(time_difference: float) -> TimeSummary:

    return TimeSummary(
        time_overall=time_difference,
        seconds=_get_time_string(time_difference % 60),
        minutes=_get_time_string(time_difference // 60),
        hours=_get_time_string(time_difference // 3600),
    )


def _get_time_string(time_difference: float) -> str:
    number_of_digits = 2

    return str(int(time_difference)).zfill(number_of_digits)


def log_summary(
    logger: Logger, jobs_summary: JobsSummary, time_summary: TimeSummary
) -> None:
    logger.info(
        f"Summary: "
        f"{jobs_summary.successful} successful, "
        f"{jobs_summary.warnings} warnings, "
        f"{jobs_summary.failed} failed in "
        f"{time_summary.time_overall}s "
        f"({time_summary.hours}:{time_summary.minutes}:{time_summary.seconds}) "
    )
