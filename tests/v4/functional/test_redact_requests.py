import uuid
from io import BytesIO

import httpx
import pytest

from redact.errors import RedactConnectError, RedactReadTimeout
from redact.v4 import JobArguments, OutputType, Region, ServiceType


@pytest.fixture
def mocked_response(mocker):
    mocked_response = mocker.Mock()
    mocked_response.status_code = 200
    mocked_response.json.return_value = {"output_id": str(uuid.uuid4())}
    return mocked_response


class TestRedactRequests:
    def test_upload_from_disk(self, redact_requests, some_image):
        # GIVEN a Redact instance and a test image
        # WHEN the image comes from disk
        # THEN it can be posted without error
        redact_requests.post_job(
            file=some_image,
            service=ServiceType.blur,
            out_type=OutputType.images,
            job_args=JobArguments(region=Region.germany),
        )

    def test_upload_from_memory(self, redact_requests, some_image):
        # GIVEN a Redact instance and a test image
        # WHEN the image comes from memory
        img = BytesIO(some_image.read())
        img.name = "in-mem.jpg"  # pretend to be a FileIO
        # THEN it can be posted without error by providing a name manually
        redact_requests.post_job(
            file=img,
            service=ServiceType.blur,
            out_type=OutputType.images,
            job_args=JobArguments(region=Region.germany),
        )

    @pytest.mark.parametrize(
        "file_size,expected_timeout", [[1, 70], [4, 100], [20, 260]]
    )
    def test_post_dynamic_timeout(
        self,
        redact_requests,
        some_image,
        mocker,
        mocked_response,
        file_size,
        expected_timeout,
    ):
        # GIVEN different file sizes
        mocker.patch(
            "redact.v4.redact_requests.get_filesize_in_gb", return_value=file_size
        )
        mocked_cls = mocker.patch.object(
            httpx.Client, "post", return_value=mocked_response
        )

        # WHEN posting a new job
        redact_requests.post_job(
            file=some_image,
            service=ServiceType.blur,
            out_type=OutputType.images,
            job_args=JobArguments(region=Region.germany),
        )

        # THEN post request was called with the correct timeout value
        _, mock_kwargs = mocked_cls.call_args
        assert mock_kwargs["timeout"] == expected_timeout

    def test_post_use_start_job_timeout(
        self, redact_requests, some_image, mocker, mocked_response
    ):
        # GIVEN start_job_timeout is set
        redact_requests.start_job_timeout = 30
        mocker.patch("redact.v4.redact_requests.get_filesize_in_gb", return_value=4)
        mocked_cls = mocker.patch.object(
            httpx.Client, "post", return_value=mocked_response
        )

        # WHEN posting a new job
        redact_requests.post_job(
            file=some_image,
            service=ServiceType.blur,
            out_type=OutputType.images,
            job_args=JobArguments(region=Region.germany),
        )

        # THEN post request was called with the start_job_timeout value
        _, mock_kwargs = mocked_cls.call_args
        assert mock_kwargs["timeout"] == 30

    def test_post_no_retry_on_read_timeout(self, redact_requests, some_image, mocker):
        # GIVEN a read timeout will be raised
        mocker.patch("redact.v4.redact_requests.get_filesize_in_gb", return_value=4)
        mocked_cls = mocker.patch.object(
            httpx.Client, "post", side_effect=httpx.ReadTimeout("read_timeout")
        )

        # WHEN posting a new job
        with pytest.raises(RedactReadTimeout):
            redact_requests.post_job(
                file=some_image,
                service=ServiceType.blur,
                out_type=OutputType.images,
                job_args=JobArguments(region=Region.germany),
            )

        # THEN no retry was made
        mocked_cls.assert_called_once()

    def test_post_retry_on_connection_timeout(
        self, redact_requests, some_image, mocker
    ):
        # GIVEN a connection timeout will be raised
        redact_requests.retry_total_time_limit = 5
        mocker.patch("redact.v4.redact_requests.get_filesize_in_gb", return_value=4)
        mocked_cls = mocker.patch.object(
            httpx.Client, "post", side_effect=httpx.ConnectTimeout("connection_timeout")
        )

        # WHEN posting a new job
        with pytest.raises(RedactConnectError):
            redact_requests.post_job(
                file=some_image,
                service=ServiceType.blur,
                out_type=OutputType.images,
                job_args=JobArguments(region=Region.germany),
            )

        # THEN retries were made
        mocked_cls.call_count == 2
