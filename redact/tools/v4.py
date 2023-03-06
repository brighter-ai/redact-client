from typing import Optional

import typer

from redact.commons.utils import setup_logging
from redact.settings import Settings
from redact.v4 import InputType, JobArguments, OutputType, Region, ServiceType
from redact.v4.tools.redact_file import redact_file as rdct_file
from redact.v4.tools.redact_folder import redact_folder as rdct_folder

settings = Settings()


app = typer.Typer()


@app.command()
def redact_file(
    file_path: str = typer.Option(...),
    output_type: OutputType = typer.Option(...),
    service: ServiceType = typer.Option(...),
    output_path: Optional[str] = typer.Option(
        None, help="[default: FILE_redacted.EXT]"
    ),
    region: Optional[Region] = typer.Option(
        None,
        help=(
            "Selects the region that license plate detection should look for and that license plate "
            "replacements will be generated for"
        ),
    ),
    face: Optional[bool] = typer.Option(
        None, help="Select whether faces should be anonymized"
    ),
    license_plate: Optional[bool] = typer.Option(
        None, help="Select whether license plates should be anonymized"
    ),
    vehicle_recorded_data: Optional[bool] = typer.Option(
        None,
        help="Used to run a job with a variety of optimizations geared toward vehicle recorded data",
    ),
    speed_optimized: Optional[bool] = typer.Option(
        None,
        help="Used to run a job faster with lower accuracy and replacement quality",
    ),
    single_frame_optimized: Optional[bool] = typer.Option(
        None,
        help="Used to run a video or archive only as a set of individual images without tracking or interpolation",
    ),
    license_plate_determination_threshold: Optional[float] = typer.Option(
        None,
        help="Set the threshold between 0 and 1 that the license plate detection models use to decide if "
        "an object is a license plate, a lower value means more likely to classifly an object as a license plate",
    ),
    face_determination_threshold: Optional[float] = typer.Option(
        None,
        help=(
            "Set the threshold between 0 and 1 that the face detection model uses to decide if "
            "an object is a face, a lower value means more likely to classifly an object as a face"
        ),
    ),
    licence_plate_custom_stamp_path: Optional[str] = typer.Option(
        None, "--custom-lp", help="Image file to use for license plate replacements"
    ),
    redact_url: str = typer.Option(
        settings.redact_online_url,
        help="Specify http address or ip of the redact instance",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        help="Pass api-key if client is being used with the cloud",
        hide_input=True,
    ),
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
    verbose_logging: bool = typer.Option(False, help="Enable very noisy logging."),
):
    setup_logging(verbose_logging)

    job_args = JobArguments(
        region=region,
        face=face,
        license_plate=license_plate,
        speed_optimized=speed_optimized,
        vehicle_recorded_data=vehicle_recorded_data,
        single_frame_optimized=single_frame_optimized,
        lp_determination_threshold=license_plate_determination_threshold,
        face_determination_threshold=face_determination_threshold,
    )

    rdct_file(
        file_path=file_path,
        output_type=output_type,
        service=service,
        job_args=job_args,
        licence_plate_custom_stamp_path=licence_plate_custom_stamp_path,
        redact_url=redact_url,
        api_key=api_key,
        output_path=output_path,
        ignore_warnings=ignore_warnings,
        skip_existing=skip_existing,
        auto_delete_job=auto_delete_job,
    )


@app.command()
def redact_folder(
    input_dir: str = typer.Option(...),
    output_dir: str = typer.Option(...),
    input_type: InputType = typer.Option(...),
    output_type: OutputType = typer.Option(...),
    service: ServiceType = typer.Option(...),
    region: Optional[Region] = typer.Option(
        None,
        help=(
            "Selects the region that license plate detection should look for and that license "
            "plate replacements will be generated for"
        ),
    ),
    face: Optional[bool] = typer.Option(
        None, help="Select whether faces should be anonymized"
    ),
    license_plate: Optional[bool] = typer.Option(
        None, help="Select whether license plates should be anonymized"
    ),
    vehicle_recorded_data: Optional[bool] = typer.Option(
        None,
        help="Used to run a job with a variety of optimizations geared toward vehicle recorded data",
    ),
    speed_optimized: Optional[bool] = typer.Option(
        None,
        help="Used to run a job faster with lower accuracy and replacement quality",
    ),
    single_frame_optimized: Optional[bool] = typer.Option(
        None,
        help="Used to run a video or archive only as a set of individual images without tracking or interpolation",
    ),
    license_plate_determination_threshold: Optional[float] = typer.Option(
        None,
        help=(
            "Set the threshold between 0 and 1 that the license plate detection models use to decide "
            "if an object is a license plate, a lower value means more likely to classifly "
            "an object as a license plate"
        ),
    ),
    face_determination_threshold: Optional[float] = typer.Option(
        None,
        help=(
            "Set the threshold between 0 and 1 that the face detection model uses to decide "
            "if an object is a face, a lower value means more likely to classifly an object "
            "as a face"
        ),
    ),
    licence_plate_custom_stamp_path: Optional[str] = typer.Option(
        None, "--custom-lp", help="Image file to use for license plate replacements"
    ),
    redact_url: str = typer.Option(
        settings.redact_online_url,
        help="Specify http address or ip of the redact instance",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        help="Pass api-key if client is being used with the cloud",
        hide_input=True,
    ),
    n_parallel_jobs: int = typer.Option(
        1, help="Number of jobs to process in parallel"
    ),
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
    setup_logging(verbose_logging)

    job_args = JobArguments(
        region=region,
        face=face,
        license_plate=license_plate,
        speed_optimized=speed_optimized,
        vehicle_recorded_data=vehicle_recorded_data,
        single_frame_optimized=single_frame_optimized,
        lp_determination_threshold=license_plate_determination_threshold,
        face_determination_threshold=face_determination_threshold,
    )

    rdct_folder(
        input_dir=input_dir,
        output_dir=output_dir,
        input_type=input_type,
        output_type=output_type,
        service=service,
        job_args=job_args,
        licence_plate_custom_stamp_path=licence_plate_custom_stamp_path,
        redact_url=redact_url,
        api_key=api_key,
        n_parallel_jobs=n_parallel_jobs,
        ignore_warnings=ignore_warnings,
        skip_existing=skip_existing,
        auto_delete_job=auto_delete_job,
        auto_delete_input_file=auto_delete_input_file,
    )
