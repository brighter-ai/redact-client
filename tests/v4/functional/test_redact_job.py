import io
import logging
from pathlib import Path
from typing import IO

import pytest
from PIL import Image
from pytest_mock import MockerFixture

from redact.api_versions import REDACT_API_VERSIONS
from redact.errors import FileDownloadError, RedactResponseError
from redact.v4 import JobArguments, JobState, RedactInstance, Region


@pytest.mark.timeout(90)
class TestRedactJob:
    def test_wait_for_status_completed(self, job):
        # GIVEN an Redact job
        # WHEN a job is started
        # THEN the job finishes after a while
        assert job.wait_until_finished().get_status().state == JobState.finished

    @pytest.mark.parametrize(
        argnames="ignore_warnings",
        argvalues=[False, True],
        ids=["do not ignore warnings", "ignore warnings"],
    )
    def test_download_result(
        self,
        any_img_redact_inst: RedactInstance,
        some_image: IO[bytes],
        ignore_warnings: bool,
    ):
        # GIVEN an image and the corresponding Redact job
        job = any_img_redact_inst.start_job(
            some_image, job_args=JobArguments(region=Region.germany)
        )

        # WHEN the job is finished and the result downloaded
        job_result = job.wait_until_finished().download_result(
            ignore_warnings=ignore_warnings
        )

        # THEN the response has the right media type
        assert job_result.media_type == "*/*"

        # AND it has the same size as the input image
        anonymized_img = Image.open(io.BytesIO(job_result.content))
        some_image.seek(0)
        original_img = Image.open(some_image)
        assert anonymized_img.size == original_img.size

    @pytest.mark.parametrize(
        argnames="ignore_warnings",
        argvalues=[False, True],
        ids=["do not ignore warnings", "ignore warnings"],
    )
    def test_download_result_into_file(
        self,
        tmp_path: Path,
        any_img_redact_inst: RedactInstance,
        some_image: IO[bytes],
        ignore_warnings: bool,
    ):
        # GIVEN an image and the corresponding Redact job
        job = any_img_redact_inst.start_job(some_image)

        output_path = (
            tmp_path
            / f"{REDACT_API_VERSIONS.v4}_{job.service}_{job.out_type}_redacted_{ignore_warnings}"  # noqa W503
        )

        # WHEN the job is finished and the result downloaded
        job_result = job.wait_until_finished().download_result_to_file(
            file=output_path, ignore_warnings=ignore_warnings
        )
        print(f"job_result {job_result}")
        logging.info(f"job_result {job_result}")

        # THEN the response exists
        assert job_result.is_file()

    @pytest.mark.parametrize(
        argnames="ignore_warnings",
        argvalues=[False, True],
        ids=["do not ignore warnings", "ignore warnings"],
    )
    def test_download_result_into_file_raises(
        self,
        tmp_path: Path,
        any_img_redact_inst: RedactInstance,
        some_image: IO[bytes],
        ignore_warnings: bool,
        mocker: MockerFixture,
    ):
        # GIVEN an image and the corresponding Redact job
        job = any_img_redact_inst.start_job(some_image)

        output_path = (
            tmp_path
            / f"{REDACT_API_VERSIONS.v4}_{job.service}_{job.out_type}_redacted_{ignore_warnings}"  # noqa W503
        )

        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.iter_bytes = mocker.MagicMock(
            return_value=Exception("Test"), side_effect=Exception("Test")
        )

        mock_httpx_client_stream_context = mocker.MagicMock()
        mock_httpx_client_stream_context.__enter__ = mocker.MagicMock(
            return_value=mock_response
        )

        # THEN the request raises the FileDownloadError
        with mocker.patch(
            f"redact.{REDACT_API_VERSIONS.v4.value}.redact_requests.httpx.Client.stream",
            return_value=mock_httpx_client_stream_context,
        ) as stream_context, pytest.raises(FileDownloadError):
            job.wait_until_finished().download_result_to_file(
                file=output_path, ignore_warnings=ignore_warnings
            )

            stream_context.assert_called_once()

    def test_delete(self, job):
        # GIVEN an Redact job

        # WHEN the job is finished and then deleted
        job.wait_until_finished()
        job.delete()

        # (wait for job to be deleted)
        with pytest.raises(RedactResponseError) as exc_info:
            while True:
                job.get_status()

        # THEN it can not be found anymore
        assert exc_info.value.status_code == 404

    def test_get_status(self, job):
        job_status = job.wait_until_finished().get_status()
        assert job_status
        assert job_status.file_name == "obama.jpeg"
        assert job_status.start_timestamp is not None
        assert job_status.error is None
        assert len(job_status.warnings) == 0

    def test_get_error(self, job):
        job_error = job.wait_until_finished().get_error()
        assert isinstance(job_error, dict)
        assert len(job_error.keys()) == 1
        error_key = list(job_error.keys())[0]
        assert error_key == "error"
        assert not job_error[error_key]
