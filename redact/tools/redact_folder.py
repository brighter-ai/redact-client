import functools
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Union

import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from redact.errors import RedactConnectError, RedactResponseError
from redact.settings import Settings
from redact.tools.redact_file import redact_file
from redact.tools.utils import (
    files_in_dir,
    is_archive,
    is_image,
    is_video,
    normalize_path,
)
from redact.v3 import InputType, JobArguments, OutputType, ServiceType

log = logging.getLogger()

settings = Settings()
log.debug(f"Settings: {settings}")


def redact_folder(
    in_dir: Union[str, Path],
    out_dir: Union[str, Path],
    input_type: InputType,
    out_type: OutputType,
    service: ServiceType,
    job_args: Optional[JobArguments] = None,
    licence_plate_custom_stamp_path: Optional[str] = None,
    redact_url: str = settings.redact_url_default,
    api_key: Optional[str] = None,
    n_parallel_jobs: int = 1,
    save_labels: bool = False,
    ignore_warnings: bool = False,
    skip_existing: bool = True,
    auto_delete_job: bool = True,
    auto_delete_input_file: bool = False,
) -> None:

    # Normalize paths, e.g.: '~/..' -> '/home'
    in_dir_path = normalize_path(in_dir)
    out_dir_path = normalize_path(out_dir)
    log.info(f"Anonymize files from {in_dir_path} ...")

    if auto_delete_input_file:
        log.warning(
            "Auto-deletion ON, files will be deleted when they were processed successfully."
        )

    # Create out_dir if not existing
    if not Path(out_dir_path).exists():
        os.makedirs(out_dir_path)

    # List of relative input paths (only img/vid)
    relative_file_paths = _get_relative_file_paths(
        in_dir=in_dir_path, input_type=input_type
    )
    log.info(f"Found {len(relative_file_paths)} {input_type.value} to process")

    # Fix input arguments to make method mappable
    worker_function = functools.partial(
        _try_redact_file_with_relative_path,
        base_dir_in=in_dir_path,
        base_dir_out=out_dir_path,
        service=service,
        out_type=out_type,
        job_args=job_args,
        licence_plate_custom_stamp_path=licence_plate_custom_stamp_path,
        redact_url=redact_url,
        api_key=api_key,
        save_labels=save_labels,
        ignore_warnings=ignore_warnings,
        skip_existing=skip_existing,
        auto_delete_job=auto_delete_job,
        auto_delete_input_file=auto_delete_input_file,
    )

    log.info(f"Starting {n_parallel_jobs} parallel jobs to anonymize files ...")
    _parallel_map(
        func=worker_function, items=relative_file_paths, n_parallel_jobs=n_parallel_jobs
    )


def _parallel_map(func, items: List, n_parallel_jobs=1) -> None:
    with logging_redirect_tqdm(), ThreadPoolExecutor(
        max_workers=n_parallel_jobs
    ) as executor:
        futures = {executor.submit(func, item): item for item in items}
        for future in tqdm.tqdm(as_completed(futures), total=len(futures)):
            item = futures[future]
            try:
                future.result()
            except Exception as e:
                log.warning(
                    f"An exception occurred while processing the following file '{item}': {e}"
                )


def _get_relative_file_paths(in_dir: Path, input_type: InputType) -> List[Path]:
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
        raise ValueError(f"Unsupported input type {input_type}.")

    relative_file_paths = [Path(fp).relative_to(in_dir) for fp in file_paths]
    return relative_file_paths


def _try_redact_file_with_relative_path(
    relative_file_path: str, base_dir_in: str, base_dir_out: str, **kwargs
) -> None:
    """This is an internal helper function to be run by a thread. We log the exceptions so they don't get lost inside
    the thread."""

    try:
        _redact_file_with_relative_path(
            relative_file_path=relative_file_path,
            base_dir_in=base_dir_in,
            base_dir_out=base_dir_out,
            **kwargs,
        )
    except RedactConnectError as e:
        log.error(f"Connection error while anonymize {relative_file_path}: {str(e)}")
    except RedactResponseError as e:
        log.error(f"Unexpected response while anonymize {relative_file_path}: {str(e)}")
    except Exception as e:
        log.debug(f"Unexpected exception: {e}", exc_info=e)
        log.error(f"Error while anonymize {relative_file_path}: {str(e)}")


def _redact_file_with_relative_path(
    relative_file_path: str, base_dir_in: str, base_dir_out: str, **kwargs
) -> None:
    """This is an internal helper function."""
    in_path = Path(base_dir_in).joinpath(relative_file_path)
    out_path = Path(base_dir_out).joinpath(relative_file_path)
    redact_file(
        file_path=in_path,
        out_path=out_path,
        waiting_time_between_job_status_checks=10,
        **kwargs,
    )
