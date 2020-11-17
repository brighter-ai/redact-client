import os

from pathlib import Path

from ips_client.data_models import OutputType, ServiceType
from ips_client.tools.anonymize_folder import anonymize_folder, InputTypes


class TestAnonymizeFolder:

    def test_all_images_in_folder_are_anonymized(self, images_path, tmp_path_factory, ips_url):

        # GIVEN an input dir (with images) and an output dir
        output_path = tmp_path_factory.mktemp('imgs_dir_out')

        # WHEN the whole folder is anonymized
        anonymize_folder(in_dir=str(images_path),
                         out_dir=str(output_path),
                         input_type=InputTypes.images,
                         out_type=OutputType.images,
                         service=ServiceType.blur,
                         save_metadata=True,
                         ips_url=ips_url)

        # THEN all images the out_dir
        files_in_in_dir = os.listdir(str(images_path))
        files_in_out_dir = os.listdir(str(output_path))
        for file in files_in_in_dir:
            assert file in files_in_out_dir

        # AND all metadata text-files are found in out_dir
        for file in files_in_in_dir:
            metadata_filename = f'{Path(file).stem}.txt'
            assert metadata_filename in files_in_out_dir

        # AND no other files have been created
        assert len(files_in_out_dir) == 2 * len(files_in_in_dir)
