import pytest

from redact.errors import RedactResponseError
from redact.settings import Settings
from redact.v4 import (
    InputType,
    JobArguments,
    OutputType,
    RedactInstance,
    RedactRequests,
    Region,
    ServiceType,
)
from redact.v4.tools.redact_file import redact_file
from redact.v4.tools.redact_folder import redact_folder

settings = Settings()
REDACT_ONLINE_URL = settings.redact_online_url


@pytest.mark.timeout(90)
class TestRequestsWithApiKey:
    def test_post_with_invalid_key_fails(self, some_image):
        # GIVEN Redact Online
        redact = RedactRequests(redact_url=REDACT_ONLINE_URL, api_key="INVALID_API_KEY")

        # WHEN a request with invalid api_key is sent
        with pytest.raises(RedactResponseError) as exception_info:
            redact.post_job(
                file=some_image,
                service=ServiceType.blur,
                out_type=OutputType.images,
                job_args=JobArguments(region=Region.germany),
            )

        # THEN the response is 401
        assert exception_info.value.response.status_code == 401

    def test_post_valid_key(self, some_image, api_key):
        # GIVEN Redact Online
        redact = RedactRequests(redact_url=REDACT_ONLINE_URL, api_key=api_key)

        # WHEN a request with valid api_key is sent
        # THEN no exception is thrown
        redact.post_job(
            file=some_image,
            service=ServiceType.blur,
            out_type=OutputType.images,
            job_args=JobArguments(region=Region.germany),
        )


@pytest.mark.timeout(90)
class TestJobWithApiKey:
    def test_job_with_invalid_api_key_fails(self, some_image):
        # GIVEN Redact Online with invalid api key
        redact = RedactInstance.create(
            service=ServiceType.blur,
            out_type=OutputType.images,
            redact_url=REDACT_ONLINE_URL,
            api_key="INVALID_API_KEY",
        )

        # WHEN a job is performed
        with pytest.raises(RedactResponseError) as exception_info:
            job = redact.start_job(
                file=some_image, job_args=JobArguments(region=Region.germany)
            )
            job.wait_until_finished()
            job.download_result()
            job.get_status()
            job.delete()

        # THEN the response is 401
        assert exception_info.value.response.status_code == 401

    def test_job_with_valid_api_key(self, some_image, api_key):
        # GIVEN Redact Online with valid api key
        redact = RedactInstance.create(
            service=ServiceType.blur,
            out_type=OutputType.images,
            redact_url=REDACT_ONLINE_URL,
            api_key=api_key,
        )

        # WHEN a job is performed
        # THEN it succeeds without error
        job = redact.start_job(
            file=some_image, job_args=JobArguments(region=Region.germany)
        )
        job.wait_until_finished()
        job.download_result()
        job.get_status()
        job.delete()


@pytest.mark.timeout(120)
class TestRedactToolsWithSubscriptionKey:
    def test_redact_file_with_invalid_api_key_fails(self, images_path):
        # GIVEN an image
        img_path = images_path.joinpath("sub_dir/img_0.png")

        # WHEN the image is anonymized through Redact Online with invalid api key
        with pytest.raises(RedactResponseError) as exception_info:
            redact_file(
                file_path=str(img_path),
                redact_url=REDACT_ONLINE_URL,
                output_type=OutputType.images,
                service=ServiceType.blur,
                job_args=JobArguments(region=Region.germany),
                api_key="INVALID_API_KEY",
            )

        # THEN the response is 401
        assert exception_info.value.response.status_code == 401

    def test_redact_file_with_valid_api_key(self, images_path, api_key):
        # GIVEN an image
        img_path = images_path.joinpath("sub_dir/img_0.png")

        # WHEN the image is anonymized through Redact Online with valid api key
        # THEN no error is thrown
        redact_file(
            file_path=str(img_path),
            redact_url=REDACT_ONLINE_URL,
            api_key=api_key,
            output_type=OutputType.images,
            service=ServiceType.blur,
            job_args=JobArguments(region=Region.germany),
        )

    def test_redact_folder_with_invalid_api_key_fails(
        self, images_path, tmp_path_factory, caplog
    ):
        # GIVEN an input dir (with images) and an output dir
        output_path = tmp_path_factory.mktemp("imgs_dir_out")

        # WHEN the folder is anonymized through Redact Online with invalid api key
        redact_folder(
            input_dir=images_path,
            output_dir=output_path,
            redact_url=REDACT_ONLINE_URL,
            input_type=InputType.images,
            output_type=OutputType.images,
            service=ServiceType.blur,
            job_args=JobArguments(region=Region.germany),
            n_parallel_jobs=1,
            api_key="INVALID_API_KEY",
        )

        # THEN the logging contains error 401 (Not Authorized)
        assert "[401 Access Denied]" in caplog.text

    def test_redact_folder_with_valid_api_key(
        self, images_path, api_key, tmp_path_factory
    ):
        # GIVEN an input dir (with images) and an output dir
        output_path = tmp_path_factory.mktemp("imgs_dir_out")

        # WHEN the folder is anonymized through Redact Online with valid api key
        redact_folder(
            input_dir=images_path,
            output_dir=output_path,
            redact_url=REDACT_ONLINE_URL,
            input_type=InputType.images,
            output_type=OutputType.images,
            service=ServiceType.blur,
            job_args=JobArguments(region=Region.germany),
            n_parallel_jobs=1,
            api_key=api_key,
        )
