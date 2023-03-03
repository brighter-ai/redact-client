from typing import Callable, List
from uuid import uuid4

import pytest

from redact.commons.summary import JobsSummary
from redact.v3 import JobState, JobStatus
from redact.v3.utils import calculate_jobs_summary


class TestSummary:
    @pytest.fixture
    def get_job_status(self) -> Callable[[JobState], JobStatus]:
        def _get_job_status(job_state: JobState) -> JobStatus:
            return JobStatus(
                output_id=uuid4(),
                state=job_state,
                warnings=["test_warning"],
                error="test_error",
            )

        return _get_job_status

    @pytest.fixture
    def get_jobs_statuses(
        self, get_job_status: Callable[[JobState], JobStatus]
    ) -> Callable[[int, int], List[JobStatus]]:
        def _get_jobs_statuses(
            number_of_failed: int = 2, number_of_finished: int = 1
        ) -> List[JobStatus]:
            return [get_job_status(JobState.failed)] * number_of_failed + [
                get_job_status(JobState.finished)
            ] * number_of_finished

        return _get_jobs_statuses

    def test_calculate_jobs_summary(
        self, get_jobs_statuses: Callable[[int, int], List[JobStatus]]
    ):
        expected_jobs_summary = JobsSummary(failed=5, warnings=3, successful=1)

        exceptions = [None] * 3

        job_statuses = get_jobs_statuses(
            expected_jobs_summary.failed - len(exceptions),
            expected_jobs_summary.successful,
        )

        actual_job_summary = calculate_jobs_summary(
            job_statuses=job_statuses, exceptions=exceptions
        )

        assert actual_job_summary.failed == expected_jobs_summary.failed
        assert actual_job_summary.successful == expected_jobs_summary.successful
        assert actual_job_summary.warnings == expected_jobs_summary.warnings
