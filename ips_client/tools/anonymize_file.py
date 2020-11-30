import logging

from pathlib import Path
from requests.exceptions import ConnectionError
from typing import Optional, Union

from ips_client.job import IPSJob, JobArguments, ServiceType, OutputType
from ips_client.settings import Settings
from ips_client.tools.utils import normalize_path


logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

settings = Settings()
log.debug(f'Settings: {settings}')


def anonymize_file(file_path: str, out_type: OutputType, service: ServiceType, job_args: JobArguments = JobArguments(),
                   ips_url: str = settings.ips_url_default, out_path: Optional[str] = None, skip_existing: bool = True,
                   save_metadata: bool = True, auto_delete_job: bool = True):
    """
    If no out_path is given, <input_filename_anonymized> will be used.
    """

    # input and output path
    file_path = normalize_path(file_path)
    out_path = _get_out_path(out_path=out_path, file_path=file_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log.debug(f'Anonymize {file_path}, writing result to {out_path} ...')

    # skip?
    if skip_existing and Path(out_path).exists():
        log.debug(f'Skipping because output already exists: {out_path}')
        return

    # anonymize
    log.debug(f'Job arguments: {job_args}')
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

    # delete job
    if auto_delete_job:
        job.delete()


def _get_out_path(out_path: Union[str, Path], file_path: Path) -> Path:
    if out_path:
        return normalize_path(out_path)
    file_path = Path(file_path)
    anonymized_path = Path(file_path.parent).joinpath(f'{file_path.stem}_anonymized{file_path.suffix}')
    return normalize_path(anonymized_path)


def _get_metadata_path(out_path: Path) -> Path:
    return out_path.parent.joinpath(out_path.stem + '.txt')
