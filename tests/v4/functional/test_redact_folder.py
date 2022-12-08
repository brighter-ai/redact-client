from pathlib import Path
from typing import Union

import pytest

from redact.v4.tools.redact_folder import redact_folder
from redact.v4 import InputType, OutputType, ServiceType
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
            in_dir=images_path,
            out_dir=output_path,
            input_type=InputType.images,
            out_type=OutputType.images,
            service=ServiceType.blur,
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

        # AND no other files have been created
        assert len(files_in_out_dir) == len(files_in_in_dir)

        assert jobs_summary.successful == NUMBER_OF_IMAGES

    @staticmethod
    def _replace_file_ext(file_path: Union[str, Path], new_ext: str = ".json") -> str:
        """/some/file.abc -> /some/file.xyz"""
        file_path = Path(file_path)
        return str(file_path.parent.joinpath(f"{file_path.stem}{new_ext}"))
