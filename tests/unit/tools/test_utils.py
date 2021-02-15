import os
import pytest

from pathlib import Path

from ips_client.tools.utils import normalize_path, files_in_dir, images_in_dir


@pytest.mark.parametrize('in_path, out_path', [
    ('./foo', str(Path(os.getcwd()).joinpath('foo'))),
])
def test_normalize_path(in_path: str, out_path: str):
    assert str(normalize_path(in_path)) == out_path


def test_files_in_dir(images_path: Path):
    # GIVEN a directory with images (ins subfolders)
    # WHEN the files are listed
    full_paths = files_in_dir(images_path, recursive=True, sort=True)
    relative_paths = [str(Path(p).relative_to(images_path)) for p in full_paths]
    # THEN all images and their subfolders are in the list
    assert relative_paths == ['sub_dir/img_0.jpg', 'sub_dir/img_1.jpg', 'sub_dir/img_2.jpg']


def test_images_in_dir(images_path: Path):
    # GIVEN a directory with images (ins subfolders)
    # WHEN the files are listed
    full_paths = images_in_dir(images_path, recursive=True, sort=True)
    relative_paths = [str(Path(p).relative_to(images_path)) for p in full_paths]
    # THEN all images and their subfolders are in the list
    assert relative_paths == ['sub_dir/img_0.jpg', 'sub_dir/img_1.jpg', 'sub_dir/img_2.jpg']
