import pytest

from pathlib import Path

from redact_client.data_models import OutputType, ServiceType
from redact_client.tools.anonymize_folder import anonymize_folder, InputType


class TestAnonymizeFolder:

    @pytest.mark.parametrize(argnames='n_parallel_jobs', argvalues=[1, 5], ids=['1 job', '5 jobs'])
    def test_all_images_in_folder_are_anonymized(self, images_path: Path, tmp_path_factory, redact_url,
                                                 n_parallel_jobs: int):

        # GIVEN an input dir (with images) and an output dir
        output_path = tmp_path_factory.mktemp('imgs_dir_out')

        # WHEN the whole folder is anonymized
        anonymize_folder(in_dir=str(images_path),
                         out_dir=str(output_path),
                         input_type=InputType.images,
                         out_type=OutputType.images,
                         service=ServiceType.blur,
                         save_labels=True,
                         redact_url=redact_url,
                         n_parallel_jobs=n_parallel_jobs)

        # THEN all input images are anonymized in the output dir
        files_in_in_dir = [str(p.relative_to(images_path)) for p in images_path.rglob('*.*')]
        files_in_out_dir = [str(p.relative_to(output_path)) for p in output_path.rglob('*.*')]
        for file in files_in_in_dir:
            assert file in files_in_out_dir

        # AND all label text-files are found in out_dir
        for file in files_in_in_dir:
            labels_filename = self._replace_file_ext(file_path=file, new_ext='.json')
            assert labels_filename in files_in_out_dir

        # AND no other files have been created
        assert len(files_in_out_dir) == 2 * len(files_in_in_dir)

    @staticmethod
    def _replace_file_ext(file_path: str, new_ext: str = '.json') -> str:
        """/some/file.abc -> /some/file.xyz"""
        file_path = Path(file_path)
        return str(file_path.parent.joinpath(f'{file_path.stem}{new_ext}'))
