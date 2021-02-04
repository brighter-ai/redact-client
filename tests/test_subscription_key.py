import pytest

from ips_client.data_models import ServiceType, OutputType, IPSResponseError
from ips_client.ips_instance import IPSInstance
from ips_client.ips_requests import IPSRequests
from ips_client.settings import Settings


settings = Settings()
IPS_ONLINE_URL = settings.ips_online_url


class TestRequestsWithSubscriptionKey:

    def test_post_with_invalid_key_fails(self, test_image):

        # GIVEN IPS Online
        ips = IPSRequests(ips_url=IPS_ONLINE_URL, subscription_key="INVALID_SUBSCRIPTION_KEY")

        # WHEN a request with invalid subscription_key is sent
        with pytest.raises(IPSResponseError) as exception_info:
            ips.post_job(file=test_image, service=ServiceType.blur, out_type=OutputType.images,)

        # THEN the response is 401
        assert exception_info.value.response.status_code == 401

    def test_post_valid_key(self, test_image, subscription_key):

        # GIVEN IPS Online
        ips = IPSRequests(ips_url=IPS_ONLINE_URL, subscription_key=subscription_key)

        # WHEN a request with valid subscription_key is sent
        # THEN no exception is thrown
        ips.post_job(file=test_image, service=ServiceType.blur, out_type=OutputType.images,)


class TestJobWithSubscriptionKey:

    def test_job_with_invalid_subscription_fails(self, test_image):

        # GIVEN IPS Online with invalid subscription key
        ips = IPSInstance(service=ServiceType.blur,
                          out_type=OutputType.images,
                          ips_url=IPS_ONLINE_URL,
                          subscription_key='INVALID_SUBSCRIPTION_KEY')

        # WHEN a job is performed
        with pytest.raises(IPSResponseError) as exception_info:
            job = ips.start_job(file=test_image)
            job.wait_until_finished()
            job.download_result()
            job.get_labels()
            job.get_status()
            job.delete()

        # THEN the response is 401
        assert exception_info.value.response.status_code == 401

    def test_job_with_valid_subscription(self, test_image, subscription_key):

        # GIVEN IPS Online with valid subscription key
        ips = IPSInstance(service=ServiceType.blur,
                          out_type=OutputType.images,
                          ips_url=IPS_ONLINE_URL,
                          subscription_key=subscription_key)

        # WHEN a job is performed
        # THEN it succeeds without error
        job = ips.start_job(file=test_image)
        job.wait_until_finished()
        job.download_result()
        #job.get_labels()  # TODO: Uncomment when label endpoint is deployed to IPS Online
        job.get_status()
        job.delete()
