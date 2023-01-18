from pathlib import Path
from typing import Union

import os
import pytest

from redact.v3.tools.redact_file import redact_file
from redact.v3.tools.redact_folder import redact_folder
from redact.v3 import InputType, OutputType, ServiceType
from tests.conftest import NUMBER_OF_IMAGES


class TestRedactFolder:
    @pytest.mark.parametrize(
        argnames="n_parallel_jobs", argvalues=[1, 5], ids=["1 job", "5 jobs"]
    )
    def test_all_images_in_folder_are_anonymized(
        self,
        images_path: Path,
        tmp_path_factory,
        redact_url,
        optional_api_key,
        n_parallel_jobs: int,
    ):

        # GIVEN an input dir (with images) and an output dir
        output_path = tmp_path_factory.mktemp("imgs_dir_out")

        # WHEN the whole folder is anonymized
        jobs_summary = redact_folder(
            input_dir=images_path,
            output_dir=output_path,
            input_type=InputType.images,
            output_type=OutputType.images,
            service=ServiceType.blur,
            save_labels=True,
            redact_url=redact_url,
            api_key=optional_api_key,
            n_parallel_jobs=n_parallel_jobs,
        )

        # THEN all input images are anonymized in the output dir
        files_in_in_dir = [
            str(p.relative_to(images_path)) for p in images_path.rglob("*.*")
        ]
        files_in_out_dir = [
            str(p.relative_to(output_path)) for p in output_path.rglob("*.*")
        ]
        for file in files_in_in_dir:
            assert file in files_in_out_dir

        # AND all label text-files are found in out_dir
        for file in files_in_in_dir:
            labels_filename = self._replace_file_ext(file_path=file, new_ext=".json")
            assert labels_filename in files_in_out_dir

        # AND no other files have been created
        assert len(files_in_out_dir) == 2 * len(files_in_in_dir)

        assert jobs_summary.successful == NUMBER_OF_IMAGES

    @staticmethod
    def _replace_file_ext(file_path: Union[str, Path], new_ext: str = ".json") -> str:
        """/some/file.abc -> /some/file.xyz"""
        file_path = Path(file_path)
        return str(file_path.parent.joinpath(f"{file_path.stem}{new_ext}"))

    def test_redact_file_video_correct_file_ending_for_overlays(
        self,
        video_path: Path,
        redact_url,
        optional_api_key,
    ):
        # GIVEN an input image, service, and output_type
        # WHEN the the file is anonymized
        redact_file(
            file_path=video_path,
            output_type=OutputType.overlays,
            service=ServiceType.blur,
            redact_url=redact_url,
            api_key=optional_api_key,
            ignore_warnings=True,
        )

        # THEN the output file has the correct file ending
        file_folder = video_path.parent
        assert len(os.listdir(file_folder)) == 2

        result_file = file_folder / f"{video_path.stem}_redacted.apng"
        assert result_file.exists()

    def test_redact_folder_video_correct_file_ending_for_overlays(
        self, video_path: Path, redact_url, optional_api_key, tmp_path_factory
    ):
        # GIVEN an input dir (with videos) and an output dir
        videos_path = video_path.parent
        output_path = tmp_path_factory.mktemp("vid_dir_out")

        redact_folder(
            input_dir=videos_path,
            output_dir=output_path,
            input_type=InputType.videos,
            output_type=OutputType.overlays,
            service=ServiceType.blur,
            redact_url=redact_url,
            api_key=optional_api_key,
            n_parallel_jobs=1,
            ignore_warnings=True,
        )

        # THEN all input images are anonymized in the output dir
        files_in_out_dir = [
            p.relative_to(output_path) for p in output_path.rglob("*.*")
        ]
        for file in files_in_out_dir:
            assert file.suffix == ".apng"
