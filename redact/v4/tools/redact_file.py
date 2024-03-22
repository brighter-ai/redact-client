import logging
import os
from pathlib import Path
from typing import Dict, Optional, Union

from redact.commons.utils import (
    normalize_path,
    ImageFolderVideoHandler,
    is_folder_with_images,
)
from redact.settings import Settings
from redact.v4 import (
    JobArguments,
    JobState,
    JobStatus,
    OutputType,
    RedactInstance,
    RedactJob,
    RedactRequests,
    ServiceType,
)

log = logging.getLogger()

settings = Settings()
log.debug(f"Settings: {settings}")


def redact_file(
    file_path: Union[str, Path],
    output_type: OutputType,
    service: ServiceType,
    job_args: Optional[JobArguments] = None,
    licence_plate_custom_stamp_path: Optional[str] = None,
    redact_url: str = settings.redact_url_default,
    output_path: Optional[Union[str, Path]] = None,
    api_key: Optional[str] = None,
    ignore_warnings: bool = False,
    skip_existing: bool = True,
    auto_delete_job: bool = True,
    auto_delete_input_file: bool = False,
    waiting_time_between_job_status_checks: Optional[float] = None,
    redact_requests_param: Optional[RedactRequests] = None,
    custom_headers: Optional[Dict[str, str]] = None,
) -> Optional[JobStatus]:
    """
    If no out_path is given, <input_filename_redacted> will be used.
    """

    # input and output path
    file_path = normalize_path(file_path)
    output_path = _get_out_path(
        output_path=output_path, file_path=file_path, output_type=output_type
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    log.debug(f"Anonymize {file_path}, writing result to {output_path} ...")

    # skip?
    if skip_existing and Path(output_path).exists():
        log.debug(f"Skipping because output already exists: {output_path}")
        return None

    # (default) job arguments
    if not job_args:
        job_args = JobArguments()
    log.debug(f"Job arguments: {job_args}")

    # custom LP stamps
    licence_plate_custom_stamp = None
    if licence_plate_custom_stamp_path:
        licence_plate_custom_stamp = open(licence_plate_custom_stamp_path, "rb")

    job_status = None

    # anonymize
    try:
        redact: RedactInstance
        if redact_requests_param:
            redact = RedactInstance(
                redact_requests_param, service=service, out_type=output_type
            )
        else:
            redact = RedactInstance.create(
                service=service,
                out_type=output_type,
                redact_url=redact_url,
                api_key=api_key,
                custom_headers=custom_headers,
            )
        with open(file_path, "rb") as file:
            job: RedactJob = redact.start_job(
                file=file,
                job_args=job_args,
                licence_plate_custom_stamp=licence_plate_custom_stamp,
            )

            log.debug(
                f"Started job for input {file_path} successfully. Output_id: {job.output_id}"
            )

        if waiting_time_between_job_status_checks is not None:
            job.wait_until_finished(waiting_time_between_job_status_checks)
        else:
            job.wait_until_finished()

        job_status = job.get_status()
        if job_status.warnings:
            for warning in job_status.warnings:
                log.warning(f"Warning for '{file_path}': {warning}")
        if job_status.state == JobState.failed:
            log.error(f"Job failed for '{file_path}': {job_status.error}")
            return job_status

        # stream result to file
        job.download_result_to_file(file=output_path, ignore_warnings=ignore_warnings)
    finally:
        if licence_plate_custom_stamp:
            licence_plate_custom_stamp.close()

    # delete input file
    if auto_delete_input_file:
        log.debug(f"Deleting {file_path}")
        Path(file_path).unlink()

    # delete job
    if auto_delete_job:
        job.delete()

    return job_status


def _get_out_path(
    output_path: Optional[Union[str, Path]], file_path: Path, output_type: OutputType
) -> Path:
    if output_path:
        return normalize_path(output_path)
    file_path = Path(file_path)
    anonymized_path = Path(file_path.parent).joinpath(
        f"{file_path.stem}_redacted{file_path.suffix}"
    )
    return normalize_path(anonymized_path)


def redact_video_as_image_folder(
    dir_path: Union[str, Path],
    output_type: OutputType,
    service: ServiceType,
    job_args: Optional[JobArguments] = None,
    licence_plate_custom_stamp_path: Optional[str] = None,
    redact_url: str = settings.redact_url_default,
    output_path: Optional[Union[str, Path]] = None,
    api_key: Optional[str] = None,
    ignore_warnings: bool = False,
    skip_existing: bool = True,
    auto_delete_job: bool = True,
    auto_delete_input_file: bool = False,
    waiting_time_between_job_status_checks: Optional[float] = None,
    redact_requests_param: Optional[RedactRequests] = None,
    custom_headers: Optional[Dict[str, str]] = None,
) -> Optional[JobStatus]:

    dir_path = normalize_path(dir_path)
    if not is_folder_with_images(dir_path):
        raise ValueError("Provide a folder when using redact_video_as_image_folder")

    if output_type in (OutputType.videos, OutputType.overlays):
        if output_path is None:
            raise ValueError(
                "Provide output_path when using redact_video_as_image_folder"
            )

        if skip_existing and os.path.exists(output_path):
            log.info(f"Skipping {dir_path} due to existing path {output_path}")
            return None

        if skip_existing is False:
            raise ValueError(
                "Cannot replace existing results when using redact_video_as_image_folder due to undefined impact to subfolders"
            )

    if output_type == OutputType.images:
        raise ValueError(
            "Cannot handle normal images when using redact_video_as_image_folder"
        )
    output_type_translation = output_type
    if output_type == OutputType.videos:
        output_type_translation = OutputType.archives
        os.makedirs(str(output_path))

    with ImageFolderVideoHandler(dir_path, output_path=output_path) as handler:
        handler.prepare_video_image_folder()

        job_status = redact_file(
            file_path=Path(handler.input_tar),
            output_type=output_type_translation,
            output_path=Path(handler.output_tar),
            service=service,
            job_args=job_args,
            licence_plate_custom_stamp_path=licence_plate_custom_stamp_path,
            redact_url=redact_url,
            api_key=api_key,
            ignore_warnings=ignore_warnings,
            skip_existing=skip_existing,
            auto_delete_job=auto_delete_job,
            auto_delete_input_file=True,
            waiting_time_between_job_status_checks=waiting_time_between_job_status_checks,
            redact_requests_param=redact_requests_param,
            custom_headers=custom_headers,
        )

        handler.remove_input_tar()
        if output_type == OutputType.videos:
            handler.unpack_and_rename_output()

        return job_status
