import os
import pytest

from pathlib import Path

from redact.data_models import OutputType, ServiceType
from redact.tools.redact_folder import redact_folder, InputType


class TestRedactFolder:
    @pytest.mark.parametrize(argnames='n_parallel_jobs', argvalues=[1, 5], ids=['1 job', '5 jobs'])
    def test_all_images_in_folder_are_anonymized(self, images_path: Path, tmp_path_factory, redact_url,
                                                 n_parallel_jobs: int):

        # GIVEN an input dir (with images) and an output dir
        output_path = tmp_path_factory.mktemp('imgs_dir_out')

        # WHEN the whole folder is anonymized
        redact_folder(in_dir=str(images_path),
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

    def test_redact_folder_videos_to_archives(self, redact_url):

        path_resources = os.path.abspath(os.path.join(os.path.dirname(__file__), "../", "resources/videos"))

        redact_folder(in_dir=str(path_resources),
                      out_dir=str(path_resources),
                      input_type=InputType.videos,
                      out_type=OutputType.archives,
                      service=ServiceType.blur,
                      save_labels=True,
                      redact_url=redact_url,
                      n_parallel_jobs=1)

        in_video_file = [p for p in Path(path_resources).rglob('*.mp4')]
        out_archive_file = [p for p in Path(path_resources).rglob('*.tar')]
        out_labels_file = [p for p in Path(path_resources).rglob('*.json')]

        assert len(in_video_file) == len(out_archive_file) == len(out_labels_file) == 1

        assert in_video_file[0].stem == out_archive_file[0].stem.replace("_redacted", "") == out_labels_file[0].stem.replace("_redacted", "")

        os.remove(out_archive_file[0])
        os.remove(out_labels_file[0])

    def test_redact_folder_archives_to_videos(self, redact_url):

        path_resources = os.path.abspath(os.path.join(os.path.dirname(__file__), "../", "resources/archives"))

        redact_folder(in_dir=str(path_resources),
                      out_dir=str(path_resources),
                      input_type=InputType.archives,
                      out_type=OutputType.videos,
                      service=ServiceType.blur,
                      save_labels=True,
                      redact_url=redact_url,
                      n_parallel_jobs=1)

        in_archive_file = [p for p in Path(path_resources).rglob('*.tar')]
        out_video_file = [p for p in Path(path_resources).rglob('*.mp4')]
        out_labels_file = [p for p in Path(path_resources).rglob('*.json')]

        assert len(in_archive_file) == len(out_video_file) == len(out_labels_file) == 1

        assert in_archive_file[0].stem == out_video_file[0].stem.replace("_redacted", "") == out_labels_file[0].stem.replace("_redacted", "")

        os.remove(out_video_file[0])
        os.remove(out_labels_file[0])
