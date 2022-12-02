import shutil
from pathlib import Path

import pytest

from redact.errors import RedactResponseError
from redact.tools.redact_folder import redact_folder
from redact.v4 import (
    InputType,
    JobArguments,
    OutputType,
    RedactInstance,
    RedactJob,
    ServiceType,
)


@pytest.fixture(scope="session")
def redact_instance_vid(redact_url: str, optional_api_key) -> RedactInstance:
    return RedactInstance.create(
        service=ServiceType.blur,
        out_type=OutputType.videos,
        redact_url=redact_url,
        api_key=optional_api_key,
    )


@pytest.fixture(scope="session")
def video_with_warning_path(resource_path: Path) -> Path:
    return resource_path.joinpath("not_starting_with_keyframe.mp4")


@pytest.fixture(scope="session")
def job_wo_keyframe(
    redact_instance_vid: RedactInstance, video_with_warning_path
) -> RedactJob:
    with open(str(video_with_warning_path), "rb") as f:
        job = redact_instance_vid.start_job(file=f)
    job.wait_until_finished()
    return job


class TestWarnings:
    def test_video_with_missing_key_frame_contains_warning(
        self, job_wo_keyframe: RedactJob
    ):

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

    @pytest.mark.parametrize(argnames="ignore_warnings", argvalues=[None, False, True])
    @pytest.mark.skip("until v4 is online")
    def test_redact_folder_with_ignore_warnings(
        self,
        redact_url: str,
        video_with_warning_path: Path,
        ignore_warnings: bool,
        tmp_path_factory,
        optional_api_key,
    ):

        # GIVEN a folder with a video that produces warnings
        tmp_in_path = tmp_path_factory.mktemp("tmp_in")
        shutil.copy2(src=str(video_with_warning_path), dst=str(tmp_in_path))

        # WHEN all videos in the folder are redacted
        tmp_out_path = tmp_path_factory.mktemp("tmp_out")
        redact_folder(
            in_dir=tmp_in_path,
            out_dir=tmp_out_path,
            input_type=InputType.videos,
            out_type=OutputType.videos,
            service=ServiceType.blur,
            job_args=JobArguments(face=False),
            redact_url=redact_url,
            api_key=optional_api_key,
            ignore_warnings=ignore_warnings,
        )

        # THEN the output folder has a video iff warnings are ignored
        output_files = len(list(tmp_out_path.glob("*")))
        expected_output_files = 1 if ignore_warnings else 0
        assert output_files == expected_output_files
