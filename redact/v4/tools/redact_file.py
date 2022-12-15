import logging
from pathlib import Path
from typing import Optional, Union

from redact.settings import Settings
from redact.commons.utils import is_image, normalize_path
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
    file_path: str,
    output_type: OutputType,
    service: ServiceType,
    job_args: Optional[JobArguments] = None,
    licence_plate_custom_stamp_path: Optional[str] = None,
    redact_url: str = settings.redact_url_default,
    output_path: Optional[str] = None,
    api_key: Optional[str] = None,
    ignore_warnings: bool = False,
    skip_existing: bool = True,
    auto_delete_job: bool = True,
    auto_delete_input_file: bool = False,
    waiting_time_between_job_status_checks: Optional[float] = None,
    redact_requests_param: Optional[RedactRequests] = None,
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
        return

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
    output_path: Union[str, Path], file_path: Path, output_type: OutputType
) -> Path:
    if output_path:
        return normalize_path(output_path)
    file_path = Path(file_path)

    file_extension = file_path.suffix
    if output_type == OutputType.labels:
        file_extension = ".json"
    elif output_type == OutputType.overlays and not is_image(file_path):
        file_extension = ".apng"

    anonymized_path = Path(file_path.parent).joinpath(
        f"{file_path.stem}_redacted{file_extension}"
    )
    return normalize_path(anonymized_path)
