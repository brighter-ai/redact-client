import logging

from pathlib import Path
from requests.exceptions import ConnectionError
from typing import Optional, Union

from ips_client.data_models import Region
from ips_client.job import IPSJob, JobArguments, ServiceType, OutputType
from ips_client.settings import Settings
from ips_client.tools.utils import normalize_path


logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

settings = Settings()
log.debug(f'Settings: {settings}')


def anonymize_file(file_path: str, out_type: OutputType, service: ServiceType, region: Region = Region.european_union,
                   face: bool = True, license_plate: bool = True, ips_url: str = settings.ips_url_default,
                   out_path: Optional[str] = None, skip_existing: bool = True, save_metadata: bool = True):
    """
    If no out_path is given, <input_filename_anonymized> will be used.
    """

    # input and output path
    file_path = normalize_path(file_path)
    out_path = _get_out_path(out_path=out_path, file_path=file_path)
    log.info(f'Anonymize {file_path}, writing result to {out_path} ...')

    # skip?
    if skip_existing and Path(out_path).exists():
        log.info(f'Skipping because output already exists: {out_path}')
        return

    # assemble job arguments
    job_args = JobArguments(region=region, face=face, license_plate=license_plate)
    log.info(f'Job arguments: {job_args}')

    # anonymize
    try:
        with open(file_path, 'rb') as file:
            job: IPSJob = IPSJob.start_new(file=file,
                                           service=service,
                                           out_type=out_type,
                                           job_args=job_args,
                                           ips_url=ips_url)
        result = job.wait_until_finished().download_result()
    except ConnectionError:
        raise ConnectionError(f'Connection error! Did you provide the proper "ips_url"? Got: {ips_url}')

    # write result
    with open(out_path, 'wb') as file:
        file.write(result.content)

    # write metadata
    if save_metadata:
        with open(_get_metadata_path(out_path), 'w') as f:
            f.write(job.get_metadata().json())


def _get_out_path(out_path: Union[str, Path], file_path: str) -> str:
    if not out_path:
        file_path = Path(file_path)
        return normalize_path(
            Path(file_path.parent).joinpath(f'{file_path.stem}_anonymized{file_path.suffix}')
        )
    return normalize_path(out_path)


def _get_metadata_path(out_path: str) -> str:
    out_path = Path(out_path)
    return str(out_path.parent.joinpath(out_path.stem + '.txt'))
