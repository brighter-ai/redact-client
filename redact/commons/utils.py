import glob
import logging
from pathlib import Path
import shutil
from typing import List, Union, Optional
import tempfile
import tarfile
import fnmatch
import os
import re

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


def is_folder_with_images(dir_path: Union[str, Path]):
    """Checks that the given path is showing a folder with at least one image."""
    if os.path.isdir(dir_path):
        if len(DirectoryImageFinder().find_images(dir_path)) > 0:
            return True
    return False


class DirectoryImageFinder:
    def __init__(self):
        self._image_re = re.compile(
            "|".join(
                [
                    fnmatch.translate("*.jpeg"),
                    fnmatch.translate("*.jpg"),
                    fnmatch.translate("*.png"),
                ]
            )
        )

    def find_images(self, directory: Union[str, Path]):
        images = []
        for f in os.listdir(os.path.abspath(directory)):
            if self.is_image(f):
                images.append(f)
        return images

    def is_image(self, f):
        return self._image_re.match(f.lower()) is not None


class ImageFolderVideoHandler(object):
    def __init__(
        self,
        input_dir_path: Union[str, Path],
        output_path: Union[str, Path],
        file_batch_size: int,
    ):
        self._input_file_names: List[str] = []
        self._input_dir_path = input_dir_path
        self._output_path = output_path
        self._file_batch_size = file_batch_size
        self._files_to_clean: List[Union[str, Path]] = []
        self._directories_to_clean: List[Union[str, Path]] = []
        self._batches: Optional[List[List[str]]] = None
        self._current_batch = -1
        self.input_tar = None
        self.output_tar = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for f in self._files_to_clean:
            if os.path.exists(f):
                os.remove(f)
        for d in self._directories_to_clean:
            if os.path.exists(d):
                shutil.rmtree(d)

    def has_more(self) -> bool:
        if self._batches is None:
            self._prepare_batches()
        return (self._current_batch + 1) < len(self._batches)

    def _prepare_batches(self):
        if not is_folder_with_images(self._input_dir_path):
            raise ValueError(
                "Provide a folder with images when using flag video_as_image_folders"
            )
        if self._input_dir_path == self._output_path:
            raise ValueError(
                "When processing video image folders, output path cannot be equal to input path."
            )

        files_in_dir = os.listdir(self._input_dir_path)
        files_in_dir.sort()
        image_finder = DirectoryImageFinder()
        input_file_names: List[str] = []
        for f in files_in_dir:
            if image_finder.is_image(f):
                input_file_names.append(f)

        if self._file_batch_size <= 0:
            self._batches = [input_file_names]
        else:
            self._batches = [
                input_file_names[i : i + self._file_batch_size]
                for i in range(0, len(input_file_names), self._file_batch_size)
            ]

    def remove_input_tar(self):
        if self.input_tar is not None and os.path.exists(self.input_tar):
            os.remove(self.input_tar)
            self.input_tar = None

    def add_directory_to_clean(self, dir: Path):
        """Add a directory that is removed with all files on exit."""
        self._directories_to_clean.append(dir)

    def remove_directory_to_clean(self, dir: Path):
        """Remove a directory from the list of dirs to remove on exit."""
        self._directories_to_clean.remove(dir)

    def prepare_video_image_folder(self):
        """Create temp files and tar the images in the given directory."""
        if self._batches is None or not self.has_more():
            raise RuntimeError("Please call has_more before prepare_video_image_folder")

        self._current_batch += 1
        current_batch = self._batches[self._current_batch].copy()
        logging.debug(
            f"Preparing next batch: {self._current_batch + 1}/{len(self._batches)} of {len(current_batch)} files."
        )

        with tempfile.NamedTemporaryFile(
            mode="w+b", dir=self._input_dir_path, delete=False, suffix=".tar"
        ) as temp_file:
            self.input_tar = temp_file.name
            self._files_to_clean.append(self.input_tar)

        with tarfile.open(self.input_tar, "w:") as tar:
            for f in current_batch:
                full_path = os.path.join(self._input_dir_path, f)
                tar.add(full_path, arcname=f)

        self.output_tar = tempfile.mktemp(suffix=".tar", dir=self._output_path)
        self._files_to_clean.append(self.output_tar)

    def unpack_and_rename_output(self):
        """After processing, ensures the (batch's) files are in the output folder and correctly named."""
        temp_folder = tempfile.mkdtemp(dir=self._output_path)
        self.add_directory_to_clean(Path(temp_folder))

        # open tarfile with the default security filter
        with tarfile.open(self.output_tar, "r") as output_tarfile:
            # TODO use filter="data" parameter when we drop 3.7 support
            output_tarfile.extractall(temp_folder)
        os.remove(self.output_tar)

        self._check_and_rename_output_files(temp_folder)
        os.rmdir(temp_folder)

    def _check_and_rename_output_files(self, temp_folder: str):
        input_images = self._batches[self._current_batch].copy()
        input_images.sort()

        image_finder = DirectoryImageFinder()
        output_images = image_finder.find_images(temp_folder)
        output_images.sort()

        if len(output_images) != len(input_images):
            raise RuntimeError(
                "Count of images in input batch and images returned from service unequal!"
            )

        # check if the renaming is still happening, and if it is, then correct here
        if not input_images == output_images:

            i = 0
            for output_image in output_images:
                os.rename(
                    os.path.join(temp_folder, output_image),
                    os.path.join(temp_folder, input_images[i]),
                )
                i = i + 1

        for image in input_images:
            shutil.move(
                os.path.join(temp_folder, image), os.path.join(self._output_path, image)
            )
