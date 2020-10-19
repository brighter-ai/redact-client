import io
import pytest

from PIL import Image

from ips_data_models import IPSJobState


class TestIPSJob:

    def test_wait_for_status_completed(self, job):
        # GIVEN an IPS job
        # WHEN a job is started
        # THEN the job finishes after a while
        assert job.start().wait_until_finished().get_status().state == IPSJobState.finished

    def test_download_result(self, job, test_image):

        # GIVEN a test image
        img = Image.open(test_image)
        test_image.seek(0)

        # WHEN a job is started and the result downloaded
        anonymized_raw = job.start().wait_until_finished().download_result()

        # THEN it has the same size as the input image
        anonymized_img = Image.open(io.BytesIO(anonymized_raw))
        assert anonymized_img.size == img.size

    def test_throws_exception_when_not_started(self, job):
        # GIVEN an IPS job
        # WHEN the job is not started yet
        # THEN methods throw exceptions
        with pytest.raises(RuntimeError):
            job.get_status()
        with pytest.raises(RuntimeError):
            job.download_result()
