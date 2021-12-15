import pytest

from io import FileIO
from pathlib import Path

from redact import RedactJob, RedactInstance, ServiceType, OutputType, \
    RedactResponseError


@pytest.fixture(scope='session')
def redact_instance_vid(redact_url: str) -> RedactInstance:
    return RedactInstance.create(service=ServiceType.blur,
                                 out_type=OutputType.videos,
                                 redact_url=redact_url)


@pytest.fixture(scope='session')
def video_with_warning(resource_path: Path) -> FileIO:
    video_path = resource_path.joinpath('videos/not_starting_with_keyframe.mp4')
    with open(str(video_path), 'rb') as f:
        yield f


@pytest.fixture(scope='session')
def job_wo_keyframe(redact_instance_vid: RedactInstance, video_with_warning: FileIO) -> RedactJob:
    job = redact_instance_vid.start_job(file=video_with_warning)
    job.wait_until_finished()
    return job


class TestWarnings:

    def test_video_with_missing_key_frame_contains_warning(self, job_wo_keyframe: RedactJob):

        # GIVEN a finished job without keyframe
        # WHEN its status is downloaded
        status = job_wo_keyframe.get_status()

        # THEN the status contains a warning
        assert status.warnings

    def test_download_of_job_with_warnings_is_blocked(self, job_wo_keyframe: RedactJob):

        # GIVEN a finished job without keyframe
        # WHEN the result is downloaded
        with pytest.raises(RedactResponseError) as e:
            job_wo_keyframe.download_result()

        # THEN the download is BLOCKED
        assert e.value.status_code == 423

    def test_warnings_can_be_ignored_when_downloading(self, job_wo_keyframe: RedactJob):
        # GIVEN a finished job without keyframe
        # WHEN the result is downloaded (with ignore_warnings=True)
        # THEN the download succeeds
        job_wo_keyframe.download_result(ignore_warnings=True)
