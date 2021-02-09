import pytest

from ips_client.data_models import ServiceType, OutputType, IPSResponseError
from ips_client.ips_instance import IPSInstance
from ips_client.ips_requests import IPSRequests
from ips_client.settings import Settings
from ips_client.tools.anonymize_file import anonymize_file
from ips_client.tools.anonymize_folder import anonymize_folder, InputType


settings = Settings()
IPS_ONLINE_URL = settings.ips_online_url


class TestRequestsWithSubscriptionKey:

    def test_post_with_invalid_key_fails(self, some_image):

        # GIVEN IPS Online
        ips = IPSRequests(ips_url=IPS_ONLINE_URL, subscription_key="INVALID_SUBSCRIPTION_KEY")

        # WHEN a request with invalid subscription_key is sent
        with pytest.raises(IPSResponseError) as exception_info:
            ips.post_job(file=some_image, service=ServiceType.blur, out_type=OutputType.images, )

        # THEN the response is 401
        assert exception_info.value.response.status_code == 401

    def test_post_valid_key(self, some_image, subscription_key):

        # GIVEN IPS Online
        ips = IPSRequests(ips_url=IPS_ONLINE_URL, subscription_key=subscription_key)

        # WHEN a request with valid subscription_key is sent
        # THEN no exception is thrown
        ips.post_job(file=some_image, service=ServiceType.blur, out_type=OutputType.images, )


class TestJobWithSubscriptionKey:

    def test_job_with_invalid_subscription_fails(self, some_image):

        # GIVEN IPS Online with invalid subscription key
        ips = IPSInstance.create(service=ServiceType.blur,
                                 out_type=OutputType.images,
                                 ips_url=IPS_ONLINE_URL,
                                 subscription_key='INVALID_SUBSCRIPTION_KEY')

        # WHEN a job is performed
        with pytest.raises(IPSResponseError) as exception_info:
            job = ips.start_job(file=some_image)
            job.wait_until_finished()
            job.download_result()
            job.get_labels()
            job.get_status()
            job.delete()

        # THEN the response is 401
        assert exception_info.value.response.status_code == 401

    def test_job_with_valid_subscription(self, some_image, subscription_key):

        # GIVEN IPS Online with valid subscription key
        ips = IPSInstance.create(service=ServiceType.blur,
                                 out_type=OutputType.images,
                                 ips_url=IPS_ONLINE_URL,
                                 subscription_key=subscription_key)

        # WHEN a job is performed
        # THEN it succeeds without error
        job = ips.start_job(file=some_image)
        job.wait_until_finished()
        job.download_result()
        #job.get_labels()  # TODO: Uncomment when label endpoint is deployed to IPS Online
        job.get_status()
        job.delete()


class TestAnonToolsWithSubscriptionKey:

    def test_anon_file_with_invalid_subscription_fails(self, images_path):

        # GIVEN an image
        img_path = images_path.joinpath('sub_dir/img_0.jpg')

        # WHEN the image is anonymized hrough IPS Online with invalid subscription
        with pytest.raises(IPSResponseError) as exception_info:
            anonymize_file(file_path=str(img_path),
                           ips_url=IPS_ONLINE_URL,
                           out_type=OutputType.images,
                           service=ServiceType.blur,
                           subscription_key='INVALID_SUBSCRIPTION_KEY')

        # THEN the response is 401
        assert exception_info.value.response.status_code == 401

    def test_anon_file_with_valid_subscription(self, images_path, subscription_key):
        # GIVEN an image
        img_path = images_path.joinpath('sub_dir/img_0.jpg')

        # WHEN the image is anonymized through IPS Online with valid subscription
        # THEN no error is thrown
        anonymize_file(file_path=str(img_path),
                       ips_url=IPS_ONLINE_URL,
                       subscription_key=subscription_key,
                       out_type=OutputType.images,
                       service=ServiceType.blur,
                       save_labels=False)

    def test_anon_folder_with_invalid_subscription_fails(self, images_path, tmp_path_factory):

        # GIVEN an input dir (with images) and an output dir
        output_path = tmp_path_factory.mktemp('imgs_dir_out')

        # WHEN the folder is anonymized through IPS Online with invalid subscription
        with pytest.raises(IPSResponseError) as exception_info:
            anonymize_folder(in_dir=str(images_path),
                             out_dir=str(output_path),
                             ips_url=IPS_ONLINE_URL,
                             input_type=InputType.images,
                             out_type=OutputType.images,
                             service=ServiceType.blur,
                             n_parallel_jobs=1,
                             subscription_key='INVALID_SUBSCRIPTION_KEY',
                             save_labels=False)

        # THEN the response is 401
        assert exception_info.value.response.status_code == 401

    def test_anon_folder_with_valid_subscription(self, images_path, subscription_key, tmp_path_factory):

        # GIVEN an input dir (with images) and an output dir
        output_path = tmp_path_factory.mktemp('imgs_dir_out')

        # WHEN the folder is anonymized hrough IPS Online with valid subscription
        anonymize_folder(in_dir=str(images_path),
                         out_dir=str(output_path),
                         ips_url=IPS_ONLINE_URL,
                         input_type=InputType.images,
                         out_type=OutputType.images,
                         service=ServiceType.blur,
                         n_parallel_jobs=1,
                         subscription_key=subscription_key,
                         save_labels = False)
