from typing import List, Optional

import typer

from redact.commons.utils import parse_key_value_pairs, setup_logging
from redact.settings import Settings
from redact.v4 import InputType, JobArguments, OutputType, Region, ServiceType
from redact.v4.tools.redact_file import (
    redact_file as rdct_file,
    redact_video_as_image_folder,
)
from redact.v4.tools.redact_folder import redact_folder as rdct_folder

settings = Settings()


app = typer.Typer()


EXPERIMENTAL = typer.style("Experimental", bold=True)
EXPERIMENTAL_WARNING = typer.style(
    "The parameter might not yet fully work with all parameters and output types.",
    bold=True,
)
AREA_OF_INTEREST_FORMAT = typer.style("x,y,width,height", bold=True)
AREA_OF_INTEREST = typer.style("'--areas_of_interest 0,0,960,540'", bold=True)
AREAS_OF_INTEREST = typer.style(
    "'--areas_of_interest 0,0,960,540 --areas_of_interest 0,540,960,540'", bold=True
)


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
        show_default=False,
    ),
    face: Optional[bool] = typer.Option(
        None, help="Select whether faces should be anonymized", show_default=False
    ),
    license_plate: Optional[bool] = typer.Option(
        None,
        help="Select whether license plates should be anonymized",
        show_default=False,
    ),
    full_body: Optional[bool] = typer.Option(
        None,
        help="Select whether full bodies should be anonymized",
        show_default=False,
    ),
    vehicle_recorded_data: Optional[bool] = typer.Option(
        None,
        help="Used to run a job with a variety of optimizations geared toward vehicle recorded data",
        show_default=False,
    ),
    speed_optimized: Optional[bool] = typer.Option(
        None,
        help="Used to run a job faster with lower accuracy and replacement quality",
        show_default=False,
    ),
    single_frame_optimized: Optional[bool] = typer.Option(
        None,
        help="Used to run a video or archive only as a set of individual images without tracking or interpolation",
        show_default=False,
    ),
    license_plate_determination_threshold: Optional[float] = typer.Option(
        None,
        help="Set the threshold between 0 and 1 that the license plate detection models use to decide if "
        "an object is a license plate, a lower value means more likely to classifly an object as a license plate",
        show_default=False,
    ),
    face_determination_threshold: Optional[float] = typer.Option(
        None,
        help=(
            "Set the threshold between 0 and 1 that the face detection model uses to decide if "
            "an object is a face, a lower value means more likely to classifly an object as a face"
        ),
        show_default=False,
    ),
    full_body_segmentation_threshold: Optional[float] = typer.Option(
        None,
        help=(
            "Set the threshold between 0 and 1 that the full body segmentation model uses to decide if "
            "an object is a full body, a lower value means more likely to classifly an object as a full body"
        ),
        show_default=False,
    ),
    licence_plate_custom_stamp_path: Optional[str] = typer.Option(
        None,
        "--custom-lp",
        help="Image file to use for license plate replacements",
        show_default=False,
    ),
    status_webhook_url: Optional[str] = typer.Option(
        None,
        "--status-webhook-url",
        help="A URL to call when the status of the Job changes",
        show_default=False,
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
        False, help="Download results even if they have warnings", show_default=False
    ),
    skip_existing: bool = typer.Option(
        True, help="Specify whether to overwrite previously run files"
    ),
    auto_delete_job: bool = typer.Option(
        True, help="Specify whether to automatically delete the job from the backend"
    ),
    verbose_logging: bool = typer.Option(False, help="Enable very noisy logging."),
    areas_of_interest: Optional[List[str]] = typer.Option(
        None,
        help=(
            f"{EXPERIMENTAL} Areas of interest's left corner coordinates x and y, their height and width. "
            f"Must be provided as a string in the following format {AREA_OF_INTEREST_FORMAT}. Multiple areas could be "
            f"added if needed. For example, {AREA_OF_INTEREST}, or {AREAS_OF_INTEREST} for the multiple areas. "
            f"{EXPERIMENTAL_WARNING}"
        ),
        show_default=False,
    ),
    custom_headers: List[str] = typer.Option(
        [],
        help="Key-value pairs in the format key=value which will be added to allr equest header",
    ),
    video_as_image_folders: bool = typer.Option(
        False,
        help="Enable processing of leaf directories with images "
        "as videos with frames in alphabetic order.",
    ),
    video_as_image_folders_batch_size: int = typer.Option(
        1500,
        help="Sets the size of the batches in images.",
    ),
):
    setup_logging(verbose_logging)

    parsed_header = parse_key_value_pairs(custom_headers)

    job_args = JobArguments(
        region=region,
        face=face,
        license_plate=license_plate,
        full_body=full_body,
        speed_optimized=speed_optimized,
        vehicle_recorded_data=vehicle_recorded_data,
        single_frame_optimized=single_frame_optimized,
        lp_determination_threshold=license_plate_determination_threshold,
        face_determination_threshold=face_determination_threshold,
        full_body_segmentation_threshold=full_body_segmentation_threshold,
        status_webhook_url=status_webhook_url,
        areas_of_interest=areas_of_interest,
    )

    if video_as_image_folders:
        redact_video_as_image_folder(
            dir_path=file_path,
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
            custom_headers=parsed_header,
            file_batch_size=video_as_image_folders_batch_size,
        )
    else:
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
            custom_headers=parsed_header,
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
        show_default=False,
    ),
    face: Optional[bool] = typer.Option(
        None, help="Select whether faces should be anonymized", show_default=False
    ),
    license_plate: Optional[bool] = typer.Option(
        None,
        help="Select whether license plates should be anonymized",
        show_default=False,
    ),
    full_body: Optional[bool] = typer.Option(
        None,
        help="Select whether full bodies should be anonymized",
        show_default=False,
    ),
    vehicle_recorded_data: Optional[bool] = typer.Option(
        None,
        help="Used to run a job with a variety of optimizations geared toward vehicle recorded data",
        show_default=False,
    ),
    speed_optimized: Optional[bool] = typer.Option(
        None,
        help="Used to run a job faster with lower accuracy and replacement quality",
        show_default=False,
    ),
    single_frame_optimized: Optional[bool] = typer.Option(
        None,
        help="Used to run a video or archive only as a set of individual images without tracking or interpolation",
        show_default=False,
    ),
    license_plate_determination_threshold: Optional[float] = typer.Option(
        None,
        help=(
            "Set the threshold between 0 and 1 that the license plate detection models use to decide "
            "if an object is a license plate, a lower value means more likely to classifly "
            "an object as a license plate"
        ),
        show_default=False,
    ),
    face_determination_threshold: Optional[float] = typer.Option(
        None,
        help=(
            "Set the threshold between 0 and 1 that the face detection model uses to decide "
            "if an object is a face, a lower value means more likely to classifly an object "
            "as a face"
        ),
        show_default=False,
    ),
    full_body_segmentation_threshold: Optional[float] = typer.Option(
        None,
        help=(
            "Set the threshold between 0 and 1 that the full body segmentation model uses to decide if "
            "an object is a full body, a lower value means more likely to classifly an object as a full body"
        ),
        show_default=False,
    ),
    licence_plate_custom_stamp_path: Optional[str] = typer.Option(
        None,
        "--custom-lp",
        help="Image file to use for license plate replacements",
        show_default=False,
    ),
    status_webhook_url: Optional[str] = typer.Option(
        None,
        "--status-webhook-url",
        help="A URL to call when the status of the Job changes",
        show_default=False,
    ),
    redact_url: List[str] = typer.Option(
        [settings.redact_online_url],
        help="Specify http address or ip of the redact instance, or multiple for client-side load balancing",
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
        False, help="Download results even if they have warnings", show_default=False
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
    areas_of_interest: Optional[List[str]] = typer.Option(
        None,
        help=(
            f"{EXPERIMENTAL} Areas of interest's left corner coordinates x and y, their height and width. "
            f"Must be provided as a string in the following format {AREA_OF_INTEREST_FORMAT}. Multiple areas could be "
            f"added if needed. For example, {AREA_OF_INTEREST}, or {AREAS_OF_INTEREST} for the multiple areas. "
            f"{EXPERIMENTAL_WARNING}"
        ),
    ),
    custom_headers: List[str] = typer.Option(
        [],
        help="Key-value pairs in the format key=value which will be added to allr equest header",
    ),
    video_as_image_folders: bool = typer.Option(
        False,
        help="Enable processing of leaf directories with images "
        "as videos with frames in alphabetic order.",
    ),
    video_as_image_folders_batch_size: int = typer.Option(
        1500,
        help="Sets the size of the batches in images.",
    ),
):
    setup_logging(verbose_logging)

    parsed_header = parse_key_value_pairs(custom_headers)

    job_args = JobArguments(
        region=region,
        face=face,
        license_plate=license_plate,
        full_body=full_body,
        speed_optimized=speed_optimized,
        vehicle_recorded_data=vehicle_recorded_data,
        single_frame_optimized=single_frame_optimized,
        lp_determination_threshold=license_plate_determination_threshold,
        face_determination_threshold=face_determination_threshold,
        full_body_segmentation_threshold=full_body_segmentation_threshold,
        status_webhook_url=status_webhook_url,
        areas_of_interest=areas_of_interest,
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
        custom_headers=parsed_header,
        video_as_image_folders=video_as_image_folders,
        video_as_image_folders_batch_size=video_as_image_folders_batch_size,
    )
