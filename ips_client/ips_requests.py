import requests
import urllib.parse

from typing import Dict, Optional, IO
from uuid import UUID

from ips_client.data_models import ServiceType, OutputType, JobArguments
from ips_client.utils import normalize_url


REQUESTS_TIMEOUT = 15


class IPSRequests:
    """
    Helper class wrapping requests to the IPS API.
    """

    API_VERSION = 'v3'

    def __init__(self, ips_url: str = 'http://127.0.0.1:8787/'):
        self.ips_url = normalize_url(ips_url)

    def post_job(self, file: IO, service: ServiceType, out_type: OutputType,
                 job_args: JobArguments = JobArguments(), file_name: Optional[str] = None) -> Dict:
        """
        Post the job via a post request.
        """

        # We need a file name with extension.
        # For file streams opened from disk, the name is available.
        # But for other streams it is not.
        if not file_name:
            try:
                file_name = file.name
            except AttributeError:
                raise ValueError('Please specify file_name (including extension)!')

        files = {'file': (file_name, file)}

        url = urllib.parse.urljoin(self.ips_url, f'/{service}/{self.API_VERSION}/{out_type}')

        response = requests.post(url=url,
                                 files=files,
                                 params=job_args.dict(),
                                 timeout=REQUESTS_TIMEOUT)

        if response.status_code != 200:
            raise RuntimeError(f'Error while posting job: {response}')

        return response.json()

    def get_output(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> bytes:

        url = urllib.parse.urljoin(self.ips_url, f'/{service}/{self.API_VERSION}/{out_type}/{output_id}')
        response = requests.get(url, timeout=REQUESTS_TIMEOUT)

        if response.status_code != 200:
            raise RuntimeError(f'Error while getting job result: {response}')

        return response.content

    def get_status(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> Dict:

        url = urllib.parse.urljoin(self.ips_url, f'/{service}/{self.API_VERSION}/{out_type}/{output_id}/status')
        response = requests.get(url, timeout=REQUESTS_TIMEOUT)

        if response.status_code != 200:
            raise RuntimeError(f'Error while getting job status: {response}')

        return response.json()

    def delete_output(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> Dict:

        url = urllib.parse.urljoin(self.ips_url, f'/{service}/{self.API_VERSION}/{out_type}/{output_id}')
        response = requests.delete(url, timeout=REQUESTS_TIMEOUT)

        if response.status_code != 200:
            raise RuntimeError(f'Error while deleting job: {response}')

        return response.json()

    def get_error(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> Dict:

        url = urllib.parse.urljoin(self.ips_url, f'/{service}/{self.API_VERSION}/{out_type}/{output_id}/error')
        response = requests.get(url, timeout=REQUESTS_TIMEOUT)

        if response.status_code != 200:
            raise RuntimeError(f'Error while getting job error: {response}')

        return response.json()
