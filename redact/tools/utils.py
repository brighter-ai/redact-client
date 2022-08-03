import glob

from pathlib import Path
from typing import List, Union

ARCHIVE_EXTENSIONS = ["tar"]
IMG_EXTENSIONS = ["jpeg", "jpg", "bmp", "png"]
VID_EXTENSIONS = ["mp4", "avi", "mov", "mkv", "mts", "ts", "webm"]


def normalize_path(path: Union[str, Path]) -> Path:
    return Path(path).expanduser().resolve()


def file_extension(path: str) -> str:
    """
    Extracts canonical file extension from path (no leading dot and all lowercase)
    e.g. mp4, avi, jpeg, ts
    """
    return Path(path).suffix[1:].lower()


def files_in_dir(dir: Path, recursive=True, sort=False) -> List[str]:
    """
    Iterates recursively through all files in all subfolders.
    """

    path = Path(dir)

    if recursive:
        search_path = str(path.joinpath("**"))
        file_list = glob.glob(search_path, recursive=True)
    else:
        search_path = str(path.joinpath("*"))
        file_list = glob.glob(search_path, recursive=False)

    file_list = [f for f in file_list if Path(f).is_file()]

    if sort:
        file_list.sort()

    return file_list


def is_archive(file_path: str) -> bool:
    """
    Determine of a given file is an archive (according to its extension).
    """
    file_ext = file_extension(file_path)
    return file_ext in ARCHIVE_EXTENSIONS


def is_image(file_path: str) -> bool:
    """
    Determine of a given file is an image (according to its extension).
    """
    file_ext = file_extension(file_path)
    return file_ext in IMG_EXTENSIONS


def is_video(file_path: str) -> bool:
    """
    Determine of a given file is an video (according to its extension).
    """
    file_ext = file_extension(file_path)
    return file_ext in VID_EXTENSIONS


def archives_in_dir(dir: Path, recursive=True, sort=False):
    """
    Iterates recursively over all archives in all subfolders.
    """
    file_list = files_in_dir(dir=dir, recursive=recursive, sort=sort)
    for file in file_list:
        if is_archive(file):
            yield file


def images_in_dir(dir: Path, recursive=True, sort=False):
    """
    Iterates recursively over all images in all subfolders.
    """
    file_list = files_in_dir(dir=dir, recursive=recursive, sort=sort)
    for file in file_list:
        if is_image(file):
            yield file


def videos_in_dir(dir: Path, recursive=True, sort=False):
    """
    Iterates recursively over all videos in all subfolders.
    """
    file_list = files_in_dir(dir=dir, recursive=recursive, sort=sort)
    for file in file_list:
        if is_video(file):
            yield file
