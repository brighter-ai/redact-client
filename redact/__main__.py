from typing import Optional
import logging

import typer

from redact.data_models import JobArguments, Region, ServiceType, OutputType
from redact.settings import Settings
from redact.tools.redact_file import redact_file as rdct_file
from redact.tools.redact_folder import redact_folder as rdct_folder
from redact.tools.redact_folder import InputType

settings = Settings()


def redact_file(
    file_path: str,
    out_type: OutputType,
    service: ServiceType,
    out_path: Optional[str] = typer.Option(None, help="[default: FILE_redacted.EXT]"),
    region: Region = typer.Option(
        Region.european_union,
        help="Selects the region that license plate detection should look for and that license plate replacements will be generated for",
    ),
    face: bool = typer.Option(True, help="Select whether faces should be anonymized"),
    license_plate: bool = typer.Option(
        True, help="Select whether license plates should be anonymized"
    ),
    custom_labels_file_path: Optional[str] = typer.Option(
        None, "--labels", help="A JSON file containing custom labels"
    ),
    vehicle_recorded_data: bool = typer.Option(
        False,
        help="Used to run a job with a variety of optimizations geared toward vehicle recorded data",
    ),
    speed_optimized: bool = typer.Option(
        False,
        help="Used to run a job faster with lower accuracy and replacement quality",
    ),
    single_frame_optimized: bool = typer.Option(
        False,
        help="Used to run a video or archive only as a set of individual images without tracking or interpolation",
    ),
    lp_determination_threshold: float = typer.Option(
        0.45,
        help="Set the threshold between 0 and 1 that the LP detection models use to decide if an object is a license plate, a lower value means more likely to classifly an object as a license plate",
    ),
    face_determination_threshold: float = typer.Option(
        0.25,
        help="Set the threshold between 0 and 1 that the face detection model uses to decide if an object is a face, a lower value means more likely to classifly an object as a face",
    ),
    licence_plate_custom_stamp_path: Optional[str] = typer.Option(
        None, "--custom-lp", help="Image file to use for license plate replacements"
    ),
    redact_url: str = typer.Option(
        settings.redact_online_url,
        help="Specify http address or ip of the redact instance",
    ),
    api_key: Optional[str] = typer.Option(
        None, help="Pass api-key if client is being used with the cloud"
    ),
    save_labels: bool = typer.Option(False, help="Save labels for PII bounding boxes"),
    ignore_warnings: bool = typer.Option(
        False,
        help="Download results even if they have warnings",
    ),
    skip_existing: bool = typer.Option(
        True, help="Specify whether to overwrite previously run files"
    ),
    auto_delete_job: bool = typer.Option(
        True, help="Specify whether to automatically delete the job from the backend"
    ),
):
    job_args = JobArguments(
        region=region,
        face=face,
        license_plate=license_plate,
        speed_optimized=speed_optimized,
        vehicle_recorded_data=vehicle_recorded_data,
        single_frame_optimized=single_frame_optimized,
        lp_determination_threshold=lp_determination_threshold,
        face_determination_threshold=face_determination_threshold,
    )

    rdct_file(
        file_path=file_path,
        out_type=out_type,
        service=service,
        job_args=job_args,
        custom_labels_file_path=custom_labels_file_path,
        licence_plate_custom_stamp_path=licence_plate_custom_stamp_path,
        redact_url=redact_url,
        api_key=api_key,
        out_path=out_path,
        ignore_warnings=ignore_warnings,
        skip_existing=skip_existing,
        save_labels=save_labels,
        auto_delete_job=auto_delete_job,
    )


def redact_file_entry_point():
    """Entry point for redact_file script as defined in 'pyproject.toml'."""
    app = typer.Typer()
    app.command()(redact_file)
    app(prog_name="redact_file")


def redact_folder(
    in_dir: str,
    out_dir: str,
    input_type: InputType,
    out_type: OutputType,
    service: ServiceType,
    region: Region = typer.Option(
        Region.european_union,
        help="Selects the region that license plate detection should look for and that license plate replacements will be generated for",
    ),
    face: bool = typer.Option(True, help="Select whether faces should be anonymized"),
    license_plate: bool = typer.Option(
        True, help="Select whether license plates should be anonymized"
    ),
    vehicle_recorded_data: bool = typer.Option(
        False,
        help="Used to run a job with a variety of optimizations geared toward vehicle recorded data",
    ),
    speed_optimized: bool = typer.Option(
        False,
        help="Used to run a job faster with lower accuracy and replacement quality",
    ),
    single_frame_optimized: bool = typer.Option(
        False,
        help="Used to run a video or archive only as a set of individual images without tracking or interpolation",
    ),
    lp_determination_threshold: float = typer.Option(
        0.45,
        help="Set the threshold between 0 and 1 that the LP detection models use to decide if an object is a license plate, a lower value means more likely to classifly an object as a license plate",
    ),
    face_determination_threshold: float = typer.Option(
        0.25,
        help="Set the threshold between 0 and 1 that the face detection model uses to decide if an object is a face, a lower value means more likely to classifly an object as a face",
    ),
    licence_plate_custom_stamp_path: Optional[str] = typer.Option(
        None, "--custom-lp", help="Image file to use for license plate replacements"
    ),
    redact_url: str = typer.Option(
        settings.redact_online_url,
        help="Specify http address or ip of the redact instance",
    ),
    api_key: Optional[str] = typer.Option(
        None, help="Pass api-key if client is being used with the cloud"
    ),
    n_parallel_jobs: int = typer.Option(
        1, help="Number of jobs to process in parellel"
    ),
    save_labels: bool = typer.Option(False, help="Save labels for PII bounding boxes"),
    ignore_warnings: bool = typer.Option(
        False,
        help="Download results even if they have warnings",
    ),
    skip_existing: bool = typer.Option(
        True, help="Specify whether to overwrite previously run files"
    ),
    auto_delete_job: bool = typer.Option(
        True, help="Specify whether to automatically delete the job from the backend"
    ),
    auto_delete_input_file: bool = typer.Option(
        False,
        help="Specify whether to automatically delete the input file "
        "from the input folder after processing of a file completed.",
    ),
    verbose_logging: bool = typer.Option(False, help="Enable very noisy logging."),
):
    job_args = JobArguments(
        region=region,
        face=face,
        license_plate=license_plate,
        speed_optimized=speed_optimized,
        vehicle_recorded_data=vehicle_recorded_data,
        single_frame_optimized=single_frame_optimized,
        lp_determination_threshold=lp_determination_threshold,
        face_determination_threshold=face_determination_threshold,
    )

    if verbose_logging:
        logging.basicConfig(
            format="%(asctime)s %(levelname)s -- %(message)s", level=logging.DEBUG
        )
    else:
        logging.basicConfig(level=settings.log_level)

    rdct_folder(
        in_dir=in_dir,
        out_dir=out_dir,
        input_type=input_type,
        out_type=out_type,
        service=service,
        job_args=job_args,
        licence_plate_custom_stamp_path=licence_plate_custom_stamp_path,
        redact_url=redact_url,
        api_key=api_key,
        n_parallel_jobs=n_parallel_jobs,
        save_labels=save_labels,
        ignore_warnings=ignore_warnings,
        skip_existing=skip_existing,
        auto_delete_job=auto_delete_job,
        auto_delete_input_file=auto_delete_input_file,
    )


def redact_folder_entry_point():
    """Entry point for redact_folder script as defined in 'pyproject.toml'."""
    app = typer.Typer()
    app.command()(redact_folder)
    app(prog_name="redact_folder")


def main():
    """Package-wide entry point for when 'python -m redact_client' is called"""
    app = typer.Typer()
    app.command()(redact_file)  # decorate functions with @app.command()
    app.command()(redact_folder)
    app(prog_name="redact_client")


if __name__ == "__main__":
    main()
