import concurrent.futures
import functools
import logging
import os
import tqdm

from enum import Enum
from pathlib import Path
from typing import List

from ips_client.data_models import IPSResponseError
from ips_client.job import JobArguments, ServiceType, OutputType
from ips_client.settings import Settings
from ips_client.tools.utils import files_in_dir, is_image, is_video, is_archive, normalize_path
from ips_client.tools.anonymize_file import anonymize_file


logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

settings = Settings()
log.debug(f'Settings: {settings}')


class InputTypes(str, Enum):
    images: str = 'images'
    videos: str = 'videos'
    archives: str = 'archives'


def anonymize_folder(in_dir: str, out_dir: str, input_type: InputTypes, out_type: OutputType, service: ServiceType,
                     job_args: JobArguments = JobArguments(), ips_url: str = settings.ips_url_default,
                     n_parallel_jobs: int = 5, save_metadata: bool = True, skip_existing: bool = True,
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
    thread_function = functools.partial(_anonymize_file_with_relative_path,
                                        base_dir_in=in_dir,
                                        base_dir_out=out_dir,
                                        service=service,
                                        out_type=out_type,
                                        job_args=job_args,
                                        ips_url=ips_url,
                                        save_metadata=save_metadata,
                                        skip_existing=skip_existing,
                                        auto_delete_job=auto_delete_job)

    log.info(f'Starting {n_parallel_jobs} parallel jobs to anonymize files ...')
    _parallel_map(func=thread_function, items=relative_file_paths, n_parallel_jobs=n_parallel_jobs)


def _parallel_map(func, items: List, n_parallel_jobs=1):
    if n_parallel_jobs <= 1:
        # Anonymize one item at a time. In principle, the ThreadPoolExecutor could do this with one worker only. But
        # this ways we don't risk losing exceptions in the thread.
        list(tqdm.tqdm(map(func, items), total=len(items)))
    else:
        # Anonymize files concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_parallel_jobs) as executor:
            list(tqdm.tqdm(executor.map(func, items), total=len(items)))


def _get_relative_file_paths(in_dir: Path, input_type: InputTypes) -> List[str]:
    """
    Return a list of all files in in_dir. But only relative to in_dir itself.

    Example: in_dir/sub/file[1-3].foo -> [sub/file1.foo, sub/file2.foo, sub/file3.foo]
    """

    file_paths: List[str] = files_in_dir(dir=in_dir)

    if input_type == InputTypes.images:
        file_paths = [fp for fp in file_paths if is_image(fp)]
    elif input_type == InputTypes.videos:
        file_paths = [fp for fp in file_paths if is_video(fp)]
    elif input_type == InputTypes.archives:
        file_paths = [fp for fp in file_paths if is_archive(fp)]
    else:
        raise ValueError(f'Unsupported input type {input_type}.')

    relative_file_paths = [Path(fp).relative_to(in_dir) for fp in file_paths]
    return relative_file_paths


def _anonymize_file_with_relative_path(relative_file_path: str, base_dir_in: str, base_dir_out: str,
                                       service: ServiceType, out_type: OutputType, job_args: JobArguments,
                                       ips_url: str, save_metadata: bool = False, skip_existing=True,
                                       auto_delete_job: bool = True):
    """This is an internal helper function to be run by a thread."""

    try:
        in_path = Path(base_dir_in).joinpath(relative_file_path)
        out_path = Path(base_dir_out).joinpath(relative_file_path)
        anonymize_file(file_path=in_path,
                       out_type=out_type,
                       service=service,
                       job_args=job_args,
                       ips_url=ips_url,
                       out_path=out_path,
                       skip_existing=skip_existing,
                       save_metadata=save_metadata,
                       auto_delete_job=auto_delete_job)
    except IPSResponseError as e:
        log.error(f'Error while anonymizing {relative_file_path}: {str(e)}')
    except Exception as e:
        log.error(f'Error while anonymizing {relative_file_path}: {str(e)}')
