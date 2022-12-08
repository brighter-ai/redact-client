from typing import Any, List, Optional

from redact.commons.summary import JobsSummary
from redact.v3 import JobState, JobStatus


def calculate_jobs_summary(
    job_statuses: List[Optional[JobStatus]], exceptions: List[Any]
) -> JobsSummary:
    jobs_summary = JobsSummary()

    for job_status in job_statuses:
        if job_status is not None:
            if job_status.warnings:
                jobs_summary.warnings += 1

            if job_status.state == JobState.failed:
                jobs_summary.failed += 1
            elif job_status.state == JobState.finished:
                jobs_summary.successful += 1

    jobs_summary.failed += len(exceptions)

    return jobs_summary
