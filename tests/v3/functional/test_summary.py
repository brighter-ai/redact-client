from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4

import pytest

from redact.tools.summary import (
    JobsSummary,
    calculate_jobs_summary,
    log_summary,
    summary,
)
from redact.v3 import JobState, JobStatus


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
        exceptions = [None] * 3
        number_of_failed = 2
        number_of_finished = 1

        job_summary = calculate_jobs_summary(
            job_statuses=get_jobs_statuses(number_of_failed, number_of_finished),
            exceptions=exceptions,
        )

        assert job_summary == JobsSummary(failed=5, warnings=3, successful=1)

    def test_log_summary(self):
        mock_logger = Mock()
        mock_logger.info = Mock()

        log_summary(mock_logger, Mock(), Mock())

        mock_logger.info.assert_called_once()

    def test_summary(self, get_jobs_statuses: Callable[[int, int], List[JobStatus]]):
        exceptions = [None] * 3
        number_of_failed = 2
        number_of_finished = 1

        jobs_statuses = get_jobs_statuses(number_of_failed, number_of_finished)

        message = (
            f"Summary: "
            f"{number_of_failed + len(exceptions)} failed, "
            f"{number_of_finished} successful, "
            f"{number_of_failed+number_of_finished} warnings in "
        )

        mock_function = Mock(return_value=(jobs_statuses, exceptions))

        mock_logger = Mock()
        mock_logger.stdout = ""

        def info(message: str) -> None:
            mock_logger.stdout = message

        mock_logger.info = info

        actual_jobs_statuses, actual_exceptions = summary(mock_logger)(mock_function)()

        assert actual_jobs_statuses == jobs_statuses
        assert actual_exceptions == exceptions
        assert message in mock_logger.stdout
