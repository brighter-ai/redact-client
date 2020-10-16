import os

from ips_data_models import IPSJobState
from ips_job import JobArguments, IPSJob


class TestIPSJob:

    def test_wait_for_status_completed(self, test_image):

        # GIVEN a running IPS instance
        ips_url = os.environ['IPS_URL']

        # WHEN a job is posted
        job_args = JobArguments(service='dnat', out_type='images')
        job = IPSJob(file=test_image, job_args=job_args, ips_url=ips_url)

        # THEN the job finishes after a while
        assert job.start().wait_until_finished().get_status().state == IPSJobState.finished
