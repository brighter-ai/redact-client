from unittest.mock import Mock

from redact.tools.summary import JobsSummary, log_summary, summary


class TestSummary:
    def test_log_summary(self):
        mock_logger = Mock()
        mock_logger.info = Mock()

        log_summary(mock_logger, Mock(), Mock())

        mock_logger.info.assert_called_once()

    def test_summary(self):
        expected_jobs_summary = JobsSummary(failed=5, warnings=3, successful=1)

        expected_part_of_message = (
            f"Summary: "
            f"{expected_jobs_summary.successful} successful, "
            f"{expected_jobs_summary.warnings} warnings, "
            f"{expected_jobs_summary.failed} failed in "
        )

        mock_logger = Mock()
        mock_logger.stdout = ""

        def info(message: str) -> None:
            mock_logger.stdout = message

        mock_logger.info = info

        mock_function = Mock(return_value=expected_jobs_summary)

        actual_jobs_summary = summary(mock_logger)(mock_function)()

        mock_function.assert_called_once()
        assert actual_jobs_summary.failed == expected_jobs_summary.failed
        assert actual_jobs_summary.successful == expected_jobs_summary.successful
        assert actual_jobs_summary.warnings == expected_jobs_summary.warnings
        assert expected_part_of_message in mock_logger.stdout
