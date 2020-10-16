import concurrent.futures
import functools
import io
import logging
import requests
import time
import tqdm
import urllib.parse

from pathlib import Path
from typing import BinaryIO, List, Optional

from tests.benchmarking.utils import files_in_dir, is_image, is_video


logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

# requests should always be used with a timeout to avoid hanging indefinitely:
# https://requests.readthedocs.io/en/master/user/quickstart/#timeouts
REQUESTS_TIMEOUT = 30


class IdentityProtectionSuite:
    """A wrapper for the IPS API. If something is missing, feel free to add it."""

    def __init__(self, host_url: str = 'http://127.0.0.1:8787/'):
        self.api_version = 'v3'
        self.host_url = host_url

    def activate_license(self, license: bytes):
        license_file = io.BytesIO(license)
        url = urllib.parse.urljoin(self.host_url, f'/services/{self.api_version}/licenses')
        response = requests.put(url=url, files={'file': license_file}, timeout=REQUESTS_TIMEOUT)
        assert response.status_code == 200
        return response

    def post_new_job(self, file: BinaryIO, job_args: JobArguments) -> requests.Response:
        url = urllib.parse.urljoin(self.host_url, f'/{job_args.service}/{self.api_version}/{job_args.out_type}')
        files = {'file': file}
        response = requests.post(url=url, files=files, params=job_args.get_query_params(), timeout=REQUESTS_TIMEOUT)
        return response

    def anonymize(self, file: BinaryIO, job_args: JobArguments) -> bytes:

        post_response = self.post_new_job(file=file, job_args=job_args)

        if post_response.status_code == 403:
            raise RuntimeError(post_response.json())

        output_id = post_response.json().get('output_id')
        if not output_id:
            raise RuntimeError(post_response)

        result_response = self.get_output(output_id=output_id, service=job_args.service, out_type=job_args.out_type)
        return result_response.content

    def get_output(self, output_id: str, service: str, out_type: str) -> requests.Response:

        url = urllib.parse.urljoin(self.host_url, f'/{service}/{self.api_version}/{out_type}/{output_id}')
        response = requests.get(url, timeout=REQUESTS_TIMEOUT)

        while response.status_code == 409:
            time.sleep(.5)
            response = requests.get(url, timeout=REQUESTS_TIMEOUT)

        if response.status_code == 404:
            raise ValueError(f'Resource with output_id {output_id} not known!')

        if response.status_code == 410:
            raise RuntimeError(f'Job has been canceled: {response.json()}')

        if response.status_code == 500:
            raise RuntimeError(f'Internal server error: {response.json()}')

        return response

    def get_status(self, output_id: str, service: str, out_type: str) -> requests.Response:
        url = urllib.parse.urljoin(self.host_url, f'/{service}/{self.api_version}/{out_type}/{output_id}/status')
        response = requests.get(url, timeout=REQUESTS_TIMEOUT)
        return response

    def delete_job(self, output_id: str, service: str, out_type: str) -> requests.Response:
        url = urllib.parse.urljoin(self.host_url, f'/{service}/{self.api_version}/{out_type}/{output_id}')
        response = requests.delete(url, timeout=REQUESTS_TIMEOUT)
        return response

    def anonymize_file(self, file_path: str, job_args: JobArguments) -> Optional[bytes]:

        # The given out_type in job_args is overwritten but that should be okay. The new API is likely to drop the
        # out_type argument (in that form) anyways.
        if job_args.out_type is None:
            if is_image(file_path):
                job_args.out_type = 'images'
            elif is_video(file_path):
                job_args.out_type = 'videos'
            else:
                log.warning(f'Skipping file because it neither seems to be image nor video: {file_path}')
                return None

        with open(file_path, 'rb') as f:
            return self.anonymize(file=f, job_args=job_args)

    def anonymize_file_to_disk(self, file_path: str, out_path: str, job_args: JobArguments, skip_existing=True):

        log.debug(f'Anonymize {file_path}, writing result to {out_path} ...')

        if skip_existing and Path(out_path).exists():
            log.debug(f'Skipping because output already exists: {out_path}')
            return

        anonymized = self.anonymize_file(file_path=file_path, job_args=job_args)

        _write_data_to_file(data=anonymized, out_path=out_path)

    def anonymize_files_to_disk(self, in_dir: str, out_dir: str, job_args: JobArguments, n_parallel_jobs=5,
                                skip_existing=True):

        # Normalize paths, e.g.: '~/..' -> '/home'
        in_dir = _normalize_path(in_dir)
        out_dir = _normalize_path(out_dir)
        log.info(f'Anonymize files from {in_dir} ...')

        # List of relative input paths (only img/vid)
        file_paths: List[str] = files_in_dir(dir=in_dir)
        file_paths = [fp for fp in file_paths if is_image(fp) or is_video(fp)]
        relative_file_paths = [Path(fp).relative_to(in_dir) for fp in file_paths]

        log.info(f'Found {len(relative_file_paths)} images/videos')

        # Fix input arguments to make method mappable
        thread_function = functools.partial(self._anonymize_file_with_relative_path_to_disk,
                                            base_dir_in=in_dir,
                                            base_dir_out=out_dir,
                                            job_args=job_args,
                                            skip_existing=skip_existing)

        # Anonymize files concurrently
        log.info(f'Starting {n_parallel_jobs} parallel jobs to anonymize files ...')
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_parallel_jobs) as executor:
            list(tqdm.tqdm(executor.map(thread_function, relative_file_paths), total=len(relative_file_paths)))

    def _anonymize_file_with_relative_path_to_disk(self, relative_file_path: str, base_dir_in: str, base_dir_out: str,
                                                   job_args: JobArguments, skip_existing=True):

        in_path = Path(base_dir_in).joinpath(relative_file_path)
        out_path = Path(base_dir_out).joinpath(relative_file_path)

        self.anonymize_file_to_disk(file_path=in_path,
                                    out_path=out_path,
                                    job_args=job_args,
                                    skip_existing=skip_existing)


def _normalize_path(path: str) -> str:
    return str(Path(path).expanduser().resolve())


def _write_data_to_file(data: bytes, out_path: str):
    out_path = _normalize_path(out_path)
    Path(out_path).parents[0].mkdir(parents=True, exist_ok=True)
    with open(out_path, 'wb') as f:
        f.write(data)
