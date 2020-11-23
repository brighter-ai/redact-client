from typing import Optional

import typer

from ips_client.data_models import JobArguments, Region, ServiceType, OutputType
from ips_client.settings import Settings
from ips_client.tools.anonymize_file import anonymize_file as anon_file


app = typer.Typer()
settings = Settings()


@app.command()
def anonymize_file(file_path: str, out_type: OutputType, service: ServiceType, region: Region = Region.european_union,
                   face: bool = True, license_plate: bool = True, ips_url: str = settings.ips_url_default,
                   out_path: Optional[str] = None, skip_existing: bool = True, save_metadata: bool = True,
                   auto_delete_job: bool = True):
    job_args = JobArguments(region=region, face=face, license_plate=license_plate)
    anon_file(file_path=file_path, out_type=out_type, service=service, job_args=job_args, ips_url=ips_url,
              out_path=out_path, skip_existing=skip_existing, save_metadata=save_metadata,
              auto_delete_job=auto_delete_job)


if __name__ == '__main__':
    app()
