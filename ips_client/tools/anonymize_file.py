import logging
import typer

from pathlib import Path
from typing import Optional

from ips_client.data_models import Region
from ips_client.job import IPSJob, JobArguments, ServiceType, OutputType
from ips_client.settings import Settings


logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

settings = Settings()
log.debug(f'Settings: {settings}')

app = typer.Typer()


@app.command()
def anonymize_file(file_path: str, out_type: OutputType, service: ServiceType, region: Region = Region.european_union,
                   face: bool = True, license_plate: bool = True, ips_url: str = settings.ips_url_default,
                   out_path: Optional[str] = None, skip_existing: bool = True, save_metadata: bool = True):
    """
    Example usage:
    python -m scripts.anonymize_file input.jpg images blur --ips-url 127.0.0.1:8787

    If no out_path is given, <input_filename_anonymized.ext> will be used.
    """

    file_path = Path(file_path)

    if not out_path:
        out_path = Path(file_path.parent).joinpath(f'{file_path.stem}_anonymized{file_path.suffix}')
    else:
        out_path = Path(out_path)

    log.info(f'Anonymize {file_path}, writing result to {out_path} ...')

    if skip_existing and Path(out_path).exists():
        log.info(f'Skipping because output already exists: {out_path}')
        return

    job_args = JobArguments(region=region, face=face, license_plate=license_plate)
    log.info(f'Job arguments: {job_args}')

    with open(file_path, 'rb') as file:
        job: IPSJob = IPSJob.start_new(file=file,
                                       service=service,
                                       out_type=out_type,
                                       job_args=job_args,
                                       ips_url=ips_url)

    result = job.wait_until_finished().download_result()

    with open(str(out_path), 'wb') as file:
        file.write(result.content)

    if save_metadata:
        metadata = job.get_metadata()
        metadata_out_path = out_path.parent.joinpath(out_path.stem + '.txt')
        with open(str(metadata_out_path), 'w') as file:
            file.write(metadata.json())


if __name__ == '__main__':
    app()
