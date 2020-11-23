import logging
import requests
import urllib.parse

from typing import Dict, Optional, IO
from uuid import UUID

from ips_client.data_models import ServiceType, OutputType, JobArguments, JobResult, IPSResponseError, JobPostResponse
from ips_client.settings import Settings
from ips_client.utils import normalize_url, get_io_filename


settings = Settings()

logging.basicConfig(level=settings.log_level)
log = logging.getLogger('ips-requests')


class IPSRequests:
    """
    Helper class wrapping requests to the IPS API.
    """

    API_VERSION = 'v3'

    def __init__(self, ips_url: str = settings.ips_url_default):
        self.ips_url = normalize_url(ips_url)

    def post_job(self, file: IO, service: ServiceType, out_type: OutputType,
                 job_args: JobArguments = JobArguments(), file_name: Optional[str] = None) -> JobPostResponse:
        """
        Post the job via a post request.
        """

        # We need a file name with extension because the media type is inferred from it.
        file_name = get_io_filename(file=file, file_name=file_name)

        files = {'file': (file_name, file)}

        url = urllib.parse.urljoin(self.ips_url, f'{service}/{self.API_VERSION}/{out_type}')

        response = requests.post(url=url,
                                 files=files,
                                 params=job_args.dict(),
                                 timeout=settings.requests_timeout)

        if response.status_code != 200:
            raise IPSResponseError(response=response, msg=f'Error posting job')

        return JobPostResponse(**response.json())

    def get_output(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> JobResult:

        url = urllib.parse.urljoin(self.ips_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}')
        response = requests.get(url, timeout=settings.requests_timeout)

        if response.status_code != 200:
            raise IPSResponseError(response=response, msg='Error downloading job result')

        return JobResult(content=response.content,
                         media_type=response.headers['Content-Type'])

    def get_status(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> Dict:

        url = urllib.parse.urljoin(self.ips_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}/status')
        response = requests.get(url, timeout=settings.requests_timeout)

        if response.status_code != 200:
            raise IPSResponseError(response=response, msg='Error getting job status')

        return response.json()

    def get_metadata(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> Dict:

        url = urllib.parse.urljoin(self.ips_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}/metadata')
        response = requests.get(url, timeout=settings.requests_timeout)

        if response.status_code != 200:
            raise IPSResponseError(response=response, msg='Error getting job metadata')

        return response.json()

    def delete_output(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> Dict:

        url = urllib.parse.urljoin(self.ips_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}')
        response = requests.delete(url, timeout=settings.requests_timeout)

        if response.status_code != 200:
            raise IPSResponseError(response=response, msg='Error deleting job')

        return response.json()

    def get_error(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> Dict:

        url = urllib.parse.urljoin(self.ips_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}/error')
        response = requests.get(url, timeout=settings.requests_timeout)

        if response.status_code != 200:
            raise IPSResponseError(response=response, msg='Error getting job error')

        return response.json()
