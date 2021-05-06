from typing import Optional

import typer

from redact.data_models import JobArguments, Region, ServiceType, OutputType
from redact.settings import Settings
from redact.tools.redact_file import redact_file as rdct_file
from redact.tools.redact_folder import redact_folder as rdct_folder
from redact.tools.redact_folder import InputType


settings = Settings()


def redact_file(file_path: str, out_type: OutputType, service: ServiceType, region: Region = Region.european_union,
                face: bool = True, license_plate: bool = True,
                licence_plate_custom_stamp_path: Optional[str] = typer.Option(None, '--custom-lp', help='Image file to use for license plate replacements'),
                custom_labels_file_path: Optional[str] = typer.Option(None, '--labels', help='A JSON file containing custom labels'),
                redact_url: str = settings.redact_url_default, api_key: Optional[str] = None,
                out_path: Optional[str] = typer.Option(None, help="[default: FILE_redacted.EXT]"),
                skip_existing: bool = True, save_labels: bool = False,
                auto_delete_job: bool = True):
    job_args = JobArguments(region=region, face=face, license_plate=license_plate)
    rdct_file(file_path=file_path, out_type=out_type, service=service, job_args=job_args,
              custom_labels_file_path=custom_labels_file_path,
              licence_plate_custom_stamp_path=licence_plate_custom_stamp_path, redact_url=redact_url,
              api_key=api_key, out_path=out_path, skip_existing=skip_existing,
              save_labels=save_labels, auto_delete_job=auto_delete_job)


def redact_file_entry_point():
    """Entry point for redact_file script as defined in 'pyproject.toml'."""
    app = typer.Typer()
    app.command()(redact_file)
    app(prog_name='redact_file')


def redact_folder(in_dir: str, out_dir: str, input_type: InputType, out_type: OutputType, service: ServiceType,
                  region: Region = Region.european_union, face: bool = True, license_plate: bool = True,
                  licence_plate_custom_stamp_path: Optional[str] = typer.Option(None, '--custom-lp', help='Image file to use for license plate replacements'),
                  redact_url: str = settings.redact_url_default, api_key: Optional[str] = None,
                  n_parallel_jobs: int = 1, save_labels: bool = False, skip_existing: bool = True,
                  auto_delete_job: bool = True):
    job_args = JobArguments(region=region, face=face, license_plate=license_plate)
    rdct_folder(in_dir=in_dir, out_dir=out_dir, input_type=input_type, out_type=out_type, service=service,
                job_args=job_args, licence_plate_custom_stamp_path=licence_plate_custom_stamp_path,
                redact_url=redact_url, api_key=api_key, n_parallel_jobs=n_parallel_jobs,
                save_labels=save_labels, skip_existing=skip_existing, auto_delete_job=auto_delete_job)


def redact_folder_entry_point():
    """Entry point for redact_folder script as defined in 'pyproject.toml'."""
    app = typer.Typer()
    app.command()(redact_folder)
    app(prog_name='redact_folder')


def main():
    """Package-wide entry point for when 'python -m redact_client' is called"""
    app = typer.Typer()
    app.command()(redact_file)  # decorate functions with @app.command()
    app.command()(redact_folder)
    app(prog_name='redact_client')


if __name__ == '__main__':
    main()
