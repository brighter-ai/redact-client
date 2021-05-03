import pytest

from redact.data_models import ServiceType, OutputType, RedactResponseError
from redact.redact_instance import RedactInstance
from redact.redact_requests import RedactRequests
from redact.settings import Settings
from redact.tools.redact_file import redact_file
from redact.tools.redact_folder import redact_folder, InputType


settings = Settings()
REDACT_ONLINE_URL = settings.redact_online_url


@pytest.mark.timeout(30)
class TestRequestsWithSubscriptionKey:

    def test_post_with_invalid_key_fails(self, some_image):

        # GIVEN Redact Online
        redact = RedactRequests(redact_url=REDACT_ONLINE_URL, subscription_key="INVALID_API_KEY")

        # WHEN a request with invalid subscription_key is sent
        with pytest.raises(RedactResponseError) as exception_info:
            redact.post_job(file=some_image, service=ServiceType.blur, out_type=OutputType.images)

        # THEN the response is 401
        assert exception_info.value.response.status_code == 401

    def test_post_valid_key(self, some_image, subscription_key):

        # GIVEN Redact Online
        redact = RedactRequests(redact_url=REDACT_ONLINE_URL, subscription_key=subscription_key)

        # WHEN a request with valid subscription_key is sent
        # THEN no exception is thrown
        redact.post_job(file=some_image, service=ServiceType.blur, out_type=OutputType.images)


@pytest.mark.timeout(30)
class TestJobWithSubscriptionKey:

    def test_job_with_invalid_subscription_fails(self, some_image):

        # GIVEN Redact Online with invalid subscription key
        redact = RedactInstance.create(service=ServiceType.blur,
                                       out_type=OutputType.images,
                                       redact_url=REDACT_ONLINE_URL,
                                       subscription_key='INVALID_API_KEY')

        # WHEN a job is performed
        with pytest.raises(RedactResponseError) as exception_info:
            job = redact.start_job(file=some_image)
            job.wait_until_finished()
            job.download_result()
            job.get_labels()
            job.get_status()
            job.delete()

        # THEN the response is 401
        assert exception_info.value.response.status_code == 401

    def test_job_with_valid_subscription(self, some_image, subscription_key):

        # GIVEN Redact Online with valid subscription key
        redact = RedactInstance.create(service=ServiceType.blur,
                                       out_type=OutputType.images,
                                       redact_url=REDACT_ONLINE_URL,
                                       subscription_key=subscription_key)

        # WHEN a job is performed
        # THEN it succeeds without error
        job = redact.start_job(file=some_image)
        job.wait_until_finished()
        job.download_result()
        # job.get_labels()  # TODO: Uncomment when label endpoint is deployed to Redact Online
        job.get_status()
        job.delete()


@pytest.mark.timeout(30)
class TestRedactToolsWithSubscriptionKey:

    def test_redact_file_with_invalid_subscription_fails(self, images_path):

        # GIVEN an image
        img_path = images_path.joinpath('sub_dir/img_0.jpg')

        # WHEN the image is anonymized through Redact Online with invalid subscription
        with pytest.raises(RedactResponseError) as exception_info:
            redact_file(file_path=str(img_path),
                        redact_url=REDACT_ONLINE_URL,
                        out_type=OutputType.images,
                        service=ServiceType.blur,
                        subscription_key='INVALID_API_KEY')

        # THEN the response is 401
        assert exception_info.value.response.status_code == 401

    def test_redact_file_with_valid_subscription(self, images_path, subscription_key):
        # GIVEN an image
        img_path = images_path.joinpath('sub_dir/img_0.jpg')

        # WHEN the image is anonymized through Redact Online with valid subscription
        # THEN no error is thrown
        redact_file(file_path=str(img_path),
                    redact_url=REDACT_ONLINE_URL,
                    subscription_key=subscription_key,
                    out_type=OutputType.images,
                    service=ServiceType.blur,
                    save_labels=False)

    def test_redact_folder_with_invalid_subscription_fails(self, images_path, tmp_path_factory, caplog):

        # GIVEN an input dir (with images) and an output dir
        output_path = tmp_path_factory.mktemp('imgs_dir_out')

        # WHEN the folder is anonymized through Redact Online with invalid subscription
        redact_folder(in_dir=str(images_path),
                      out_dir=str(output_path),
                      redact_url=REDACT_ONLINE_URL,
                      input_type=InputType.images,
                      out_type=OutputType.images,
                      service=ServiceType.blur,
                      n_parallel_jobs=1,
                      subscription_key='INVALID_API_KEY',
                      save_labels=False)

        # THEN the logging contains error 401 (Not Authorized)
        assert '[401 Access Denied]' in caplog.text

    def test_redact_folder_with_valid_subscription(self, images_path, subscription_key, tmp_path_factory):

        # GIVEN an input dir (with images) and an output dir
        output_path = tmp_path_factory.mktemp('imgs_dir_out')

        # WHEN the folder is anonymized through Redact Online with valid subscription
        redact_folder(in_dir=str(images_path),
                      out_dir=str(output_path),
                      redact_url=REDACT_ONLINE_URL,
                      input_type=InputType.images,
                      out_type=OutputType.images,
                      service=ServiceType.blur,
                      n_parallel_jobs=1,
                      subscription_key=subscription_key,
                      save_labels=False)
