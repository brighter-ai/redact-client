import concurrent.futures
import functools
import logging
import os
import tqdm

from enum import Enum
from pathlib import Path
from typing import List, Optional

from redact_client.data_models import RedactResponseError, JobArguments
from redact_client.job import ServiceType, OutputType
from redact_client.settings import Settings
from redact_client.tools.utils import files_in_dir, is_image, is_video, is_archive, normalize_path
from redact_client.tools.anonymize_file import anonymize_file


logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

settings = Settings()
log.debug(f'Settings: {settings}')


class InputType(str, Enum):
    images: str = 'images'
    videos: str = 'videos'
    archives: str = 'archives'


def anonymize_folder(in_dir: str, out_dir: str, input_type: InputType, out_type: OutputType, service: ServiceType,
                     job_args: Optional[JobArguments] = None, licence_plate_custom_stamp_path: Optional[str] = None,
                     redact_url: str = settings.redact_url_default, subscription_key: Optional[str] = None,
                     n_parallel_jobs: int = 5, save_labels: bool = False, skip_existing: bool = True,
                     auto_delete_job: bool = True):

    # Normalize paths, e.g.: '~/..' -> '/home'
    in_dir = normalize_path(in_dir)
    out_dir = normalize_path(out_dir)
    log.info(f'Anonymize files from {in_dir} ...')

    # Create out_dir if not existing
    if not Path(out_dir).exists():
        os.makedirs(out_dir)

    # List of relative input paths (only img/vid)
    relative_file_paths = _get_relative_file_paths(in_dir=in_dir, input_type=input_type)
    log.info(f'Found {len(relative_file_paths)} {input_type.value} to process')

    # Fix input arguments to make method mappable
    thread_function = _anon_file_with_relative_path if n_parallel_jobs == 1 else _anon_file_with_relative_path_log_exc
    partial_thread_function = functools.partial(thread_function,
                                                base_dir_in=in_dir,
                                                base_dir_out=out_dir,
                                                service=service,
                                                out_type=out_type,
                                                job_args=job_args,
                                                licence_plate_custom_stamp_path=licence_plate_custom_stamp_path,
                                                redact_url=redact_url,
                                                subscription_key=subscription_key,
                                                save_labels=save_labels,
                                                skip_existing=skip_existing,
                                                auto_delete_job=auto_delete_job)

    log.info(f'Starting {n_parallel_jobs} parallel jobs to anonymize files ...')
    _parallel_map(func=partial_thread_function, items=relative_file_paths, n_parallel_jobs=n_parallel_jobs)


def _parallel_map(func, items: List, n_parallel_jobs=1):
    if n_parallel_jobs <= 1:
        # Anonymize one item at a time. In principle, the ThreadPoolExecutor could do this with one worker only. But
        # this ways we don't risk losing exceptions in the thread.
        list(tqdm.tqdm(map(func, items), total=len(items)))
    else:
        # Anonymize files concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_parallel_jobs) as executor:
            list(tqdm.tqdm(executor.map(func, items), total=len(items)))


def _get_relative_file_paths(in_dir: Path, input_type: InputType) -> List[str]:
    """
    Return a list of all files in in_dir. But only relative to in_dir itself.

    Example: in_dir/sub/file[1-3].foo -> [sub/file1.foo, sub/file2.foo, sub/file3.foo]
    """

    file_paths: List[str] = files_in_dir(dir=in_dir)

    if input_type == InputType.images:
        file_paths = [fp for fp in file_paths if is_image(fp)]
    elif input_type == InputType.videos:
        file_paths = [fp for fp in file_paths if is_video(fp)]
    elif input_type == InputType.archives:
        file_paths = [fp for fp in file_paths if is_archive(fp)]
    else:
        raise ValueError(f'Unsupported input type {input_type}.')

    relative_file_paths = [Path(fp).relative_to(in_dir) for fp in file_paths]
    return relative_file_paths


def _anon_file_with_relative_path_log_exc(relative_file_path: str, base_dir_in: str, base_dir_out: str, **kwargs):
    """This is an internal helper function to be run by a thread. We log the exceptions so they don't get lost inside
    the thread."""

    try:
        _anon_file_with_relative_path(relative_file_path=relative_file_path,
                                      base_dir_in=base_dir_in,
                                      base_dir_out=base_dir_out,
                                      **kwargs)
    except RedactResponseError as e:
        log.error(f'Error while anonymizing {relative_file_path}: {str(e)}')
    except Exception as e:
        log.error(f'Error while anonymizing {relative_file_path}: {str(e)}')


def _anon_file_with_relative_path(relative_file_path: str, base_dir_in: str, base_dir_out: str, **kwargs):
    """This is an internal helper function."""
    in_path = Path(base_dir_in).joinpath(relative_file_path)
    out_path = Path(base_dir_out).joinpath(relative_file_path)
    anonymize_file(file_path=in_path, out_path=out_path, **kwargs)
