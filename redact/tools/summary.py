import functools
import time
from logging import Logger
from typing import Any, Callable, List, Optional, Tuple

from pydantic import BaseModel

from redact.v3 import JobState, JobStatus


class JobsSummary(BaseModel):
    failed: int = 0
    warnings: int = 0
    successful: int = 0

    def __eq__(self, other):
        return (
            self.failed == other.failed  # noqa: W503
            and self.warnings == other.warnings  # noqa: W503
            and self.successful == other.successful  # noqa: W503
        )


class TimeSummary(BaseModel):
    time_overall: float
    seconds: str
    minutes: str
    hours: str

    def __eq__(self, other):
        return (
            self.time_overal == other.time_overall  # noqa: W503
            and self.seconds == other.seconds  # noqa: W503
            and self.minutes == other.minutes  # noqa: W503
            and self.hours == other.hours  # noqa: W503
        )


JobStatuses = Tuple[List[Optional[JobStatus]], Any]
RedactFolder = RedactFolderWrapper = Callable[..., JobStatuses]


def summary(logger: Logger) -> Callable[[RedactFolder], RedactFolderWrapper]:
    def decorator(redact_folder: RedactFolder) -> RedactFolderWrapper:
        @functools.wraps(redact_folder)
        def wrapper(*args: Any, **kwargs: Any) -> JobStatuses:
            start_time = time.time()

            job_statuses, exceptions = redact_folder(*args, **kwargs)

            end_time = time.time()
            time_difference = round(end_time - start_time, 1)

            jobs_summary = calculate_jobs_summary(job_statuses, exceptions)
            time_summary = calculate_time_summary(time_difference)

            log_summary(logger, jobs_summary, time_summary)

            return job_statuses, exceptions

        return wrapper

    return decorator


def calculate_jobs_summary(
    job_statuses: List[Optional[JobStatus]], exceptions: List[Any]
) -> JobsSummary:
    results = JobsSummary()

    for job_status in job_statuses:
        if job_status is not None:
            if job_status.warnings:
                results.warnings += 1

            if job_status.state == JobState.failed:
                results.failed += 1
            elif job_status.state == JobState.finished:
                results.successful += 1

    results.failed += len(exceptions)

    return results


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
        f"{jobs_summary.failed} failed, "
        f"{jobs_summary.successful} successful, "
        f"{jobs_summary.warnings} warnings in "
        f"{time_summary.time_overall}s "
        f"({time_summary.hours}:{time_summary.minutes}:{time_summary.seconds}) "
    )
