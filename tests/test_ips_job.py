import io
import pytest

from PIL import Image

from ips_client.data_models import JobState


class TestIPSJob:

    def test_wait_for_status_completed(self, job):
        # GIVEN an IPS job
        # WHEN a job is started
        # THEN the job finishes after a while
        assert job.start().wait_until_finished().get_status().state == JobState.finished

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

    @pytest.mark.timeout(5)
    def test_delete(self, job):

        # GIVEN an IPS job

        # WHEN the job is finished and then deleted
        job.start().wait_until_finished()
        job.delete()

        # (wait for job to be deleted)
        while True:
            try:
                job.get_status()
            except RuntimeError:
                break

        # THEN it can not be found anymore
        with pytest.raises(RuntimeError) as e:
            job.get_status()
        assert '404' in str(e)
