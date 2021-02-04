from typing import Optional

import typer

from ips_client.data_models import JobArguments, Region, ServiceType, OutputType
from ips_client.settings import Settings
from ips_client.tools.anonymize_file import anonymize_file as anon_file
from ips_client.tools.anonymize_folder import InputType, anonymize_folder as anon_folder


settings = Settings()


def anonymize_file(file_path: str, out_type: OutputType, service: ServiceType, region: Region = Region.european_union,
                   face: bool = True, license_plate: bool = True, ips_url: str = settings.ips_url_default,
                   subscription_key: Optional[str] = None, out_path: Optional[str] = None,
                   skip_existing: bool = True, save_labels: bool = True, auto_delete_job: bool = True):
    job_args = JobArguments(region=region, face=face, license_plate=license_plate)
    anon_file(file_path=file_path, out_type=out_type, service=service, job_args=job_args, ips_url=ips_url,
              subscription_key=subscription_key, out_path=out_path, skip_existing=skip_existing,
              save_labels=save_labels, auto_delete_job=auto_delete_job)


def anonymize_file_entry_point():
    """Entry point for ips_anon_file script as defined in 'pyproject.toml'."""
    app = typer.Typer()
    app.command()(anonymize_file)
    app(prog_name='ips_anon_file')


def anonymize_folder(in_dir: str, out_dir: str, input_type: InputType, out_type: OutputType, service: ServiceType,
                     region: Region = Region.european_union, face: bool = True, license_plate: bool = True,
                     ips_url: str = settings.ips_url_default, subscription_key: Optional[str] = None,
                     n_parallel_jobs: int = 5, save_labels: bool = True, skip_existing: bool = True,
                     auto_delete_job: bool = True):
    job_args = JobArguments(region=region, face=face, license_plate=license_plate)
    anon_folder(in_dir=in_dir, out_dir=out_dir, input_type=input_type, out_type=out_type, service=service,
                job_args=job_args, ips_url=ips_url, subscription_key=subscription_key, n_parallel_jobs=n_parallel_jobs,
                save_labels=save_labels, skip_existing=skip_existing, auto_delete_job=auto_delete_job)


def anonymize_folder_entry_point():
    """Entry point for ips_anon_folder script as defined in 'pyproject.toml'."""
    app = typer.Typer()
    app.command()(anonymize_folder)
    app(prog_name='ips_anon_folder')


def main():
    """Package-wide entry point for when 'python -m ips_client' is called"""
    app = typer.Typer()
    app.command()(anonymize_file)  # decorate functions with @app.command()
    app.command()(anonymize_folder)
    app(prog_name='ips_client')


if __name__ == '__main__':
    main()
