import glob
import logging
import math
import os
from io import BufferedReader, BytesIO, FileIO
from pathlib import Path
from typing import List, Union

from redact.settings import Settings

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


def setup_logging(verbose_logging: bool) -> None:
    format = "%(asctime)s | %(levelname)s | %(message)s"
    level = logging.DEBUG if verbose_logging else Settings().log_level

    logging.basicConfig(format=format, level=level)


def parse_key_value_pairs(kv_pairs: List[str]) -> dict:
    """Parse a list of key-value strings into a dictionary with error handling."""
    result = {}
    for item in kv_pairs:
        # Check if the item contains an equal sign
        if "=" not in item:
            raise ValueError(
                f"Invalid key-value pair: {item}. Expected format: key=value"
            )

        key, value = item.split("=", 1)  # Split only on the first equal sign

        # Validate key and value
        if not key:
            raise ValueError(f"Empty key in pair: {item}")
        if not value:
            raise ValueError(f"Empty value in pair: {item}")

        result[key] = value

    return result


def get_filesize_in_gb(file: Union[FileIO, BytesIO, BufferedReader]):
    if isinstance(file, FileIO) or isinstance(file, BufferedReader):
        file_size = os.fstat(file.fileno()).st_size
    elif isinstance(file, BytesIO):
        file_size = len(file.getbuffer())
    else:
        raise ValueError("Only FileIO, BytesIO or BufferedReader are supported.")

    return math.ceil(file_size / (1024 * 1024 * 1024))
