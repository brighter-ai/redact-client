import logging
from pathlib import Path
from typing import Optional, Union

from redact.v3 import (
    JobArguments,
    JobLabels,
    OutputType,
    RedactInstance,
    RedactJob,
    RedactRequests,
    ServiceType,
)
from redact.settings import Settings
from redact.tools.utils import normalize_path

log = logging.getLogger()

settings = Settings()
log.debug(f"Settings: {settings}")


def redact_file(
    file_path: str,
    out_type: OutputType,
    service: ServiceType,
    job_args: Optional[JobArguments] = None,
    licence_plate_custom_stamp_path: Optional[str] = None,
    custom_labels_file_path: Optional[str] = None,
    redact_url: str = settings.redact_url_default,
    out_path: Optional[str] = None,
    api_key: Optional[str] = None,
    ignore_warnings: bool = False,
    skip_existing: bool = True,
    save_labels: bool = False,
    auto_delete_job: bool = True,
    auto_delete_input_file: bool = False,
    waiting_time_between_job_status_checks: Optional[float] = None,
    redact_requests_param: Optional[RedactRequests] = None,
):
    """
    If no out_path is given, <input_filename_redacted> will be used.
    """

    # input and output path
    file_path = normalize_path(file_path)
    out_path = _get_out_path(out_path=out_path, file_path=file_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log.debug(f"Anonymize {file_path}, writing result to {out_path} ...")

    # skip?
    if skip_existing and Path(out_path).exists():
        log.debug(f"Skipping because output already exists: {out_path}")
        return

    # (default) job arguments
    if not job_args:
        job_args = JobArguments()
    log.debug(f"Job arguments: {job_args}")

    # custom labels
    custom_labels = None
    if custom_labels_file_path:
        custom_labels = JobLabels.parse_file(custom_labels_file_path)

    # custom LP stamps
    licence_plate_custom_stamp = None
    if licence_plate_custom_stamp_path:
        licence_plate_custom_stamp = open(licence_plate_custom_stamp_path, "rb")

    # anonymize
    try:
        redact: RedactInstance
        if redact_requests_param:
            redact = RedactInstance(
                redact_requests_param, service=service, out_type=out_type
            )
        else:
            redact = RedactInstance.create(
                service=service,
                out_type=out_type,
                redact_url=redact_url,
                api_key=api_key,
            )
        with open(file_path, "rb") as file:
            job: RedactJob = redact.start_job(
                file=file,
                job_args=job_args,
                licence_plate_custom_stamp=licence_plate_custom_stamp,
                custom_labels=custom_labels,
            )

            log.debug(
                f"Started job for input {file_path} successfully. Output_id: {job.output_id}"
            )

        if waiting_time_between_job_status_checks is not None:
            job.wait_until_finished(waiting_time_between_job_status_checks)
        else:
            job.wait_until_finished()

        # stream result to file
        job.download_result_to_file(file=out_path, ignore_warnings=ignore_warnings)
    finally:
        if licence_plate_custom_stamp:
            licence_plate_custom_stamp.close()

    # write labels
    if save_labels:
        labels = job.get_labels().json()
        with open(_get_labels_path(out_path), "w") as f:
            f.write(labels)

    # delete input file
    if auto_delete_input_file:
        log.debug(f"Deleting {file_path}")
        Path(file_path).unlink()

    # delete job
    if auto_delete_job:
        job.delete()


def _get_out_path(out_path: Union[str, Path], file_path: Path) -> Path:
    if out_path:
        return normalize_path(out_path)
    file_path = Path(file_path)
    anonymized_path = Path(file_path.parent).joinpath(
        f"{file_path.stem}_redacted{file_path.suffix}"
    )
    return normalize_path(anonymized_path)


def _get_labels_path(out_path: Path) -> Path:
    return out_path.parent.joinpath(out_path.stem + ".json")
