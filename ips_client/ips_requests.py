import logging
import requests
import urllib.parse

from io import FileIO
from typing import Dict, Optional, IO, Union
from uuid import UUID

from ips_client.data_models import ServiceType, OutputType, JobArguments, JobResult, IPSResponseError, JobPostResponse, \
    JobLabels
from ips_client.settings import Settings
from ips_client.utils import normalize_url


settings = Settings()

logging.basicConfig(level=settings.log_level.upper())
log = logging.getLogger('ips-requests')


class IPSRequests:
    """
    Helper class wrapping requests to the IPS API.
    """

    API_VERSION = 'v3'

    def __init__(self, ips_url: str = settings.ips_url_default, subscription_key: Optional[str] = None):

        self.ips_url = normalize_url(ips_url)
        self.subscription_key = subscription_key

        self._headers = {'Accept': '*/*'}
        if subscription_key:
            self._headers['ips-subscription-key'] = self.subscription_key

    def post_job(self, file: FileIO, service: ServiceType, out_type: OutputType,
                 job_args: Optional[JobArguments] = None, licence_plate_custom_stamp: Optional[IO] = None,
                 custom_labels: Optional[Union[str, IO, JobLabels]] = None) \
            -> JobPostResponse:
        """
        Post the job via a post request.
        """

        url = urllib.parse.urljoin(self.ips_url, f'{service}/{self.API_VERSION}/{out_type}')

        if not job_args:
            job_args = JobArguments()

        try:
            _ = file.name
        except AttributeError:
            raise ValueError("Expecting 'file' argument to have a 'name' attribute, i.e., FileIO.")

        files = {'file': file}
        if licence_plate_custom_stamp:
            files['licence_plate_custom_stamp'] = licence_plate_custom_stamp
        if custom_labels:
            files['custom_labels'] = custom_labels.json() if isinstance(custom_labels, JobLabels) else custom_labels

        response = requests.post(url=url,
                                 files=files,
                                 headers=self._headers,
                                 params=job_args.dict(),
                                 timeout=settings.requests_timeout_files)

        if response.status_code != 200:
            raise IPSResponseError(response=response, msg='Error posting job')

        return JobPostResponse(**response.json())

    def get_output(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> JobResult:

        url = urllib.parse.urljoin(self.ips_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}')
        response = requests.get(url, headers=self._headers, timeout=settings.requests_timeout_files)

        if response.status_code != 200:
            raise IPSResponseError(response=response, msg='Error downloading job result')

        return JobResult(content=response.content,
                         media_type=response.headers['Content-Type'])

    def get_status(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> Dict:

        url = urllib.parse.urljoin(self.ips_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}/status')
        response = requests.get(url, headers=self._headers, timeout=settings.requests_timeout)

        if response.status_code != 200:
            raise IPSResponseError(response=response, msg='Error getting job status')

        return response.json()

    def get_labels(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> JobLabels:

        url = urllib.parse.urljoin(self.ips_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}/labels')
        response = requests.get(url, headers=self._headers, timeout=settings.requests_timeout)

        if response.status_code != 200:
            raise IPSResponseError(response=response, msg='Error getting labels')

        return JobLabels.parse_obj(response.json())

    def delete_output(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> Dict:

        url = urllib.parse.urljoin(self.ips_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}')
        response = requests.delete(url, headers=self._headers, timeout=settings.requests_timeout)

        if response.status_code != 200:
            raise IPSResponseError(response=response, msg='Error deleting job')

        return response.json()

    def get_error(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> Dict:

        url = urllib.parse.urljoin(self.ips_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}/error')
        response = requests.get(url, timeout=settings.requests_timeout)

        if response.status_code != 200:
            raise IPSResponseError(response=response, msg='Error getting job error')

        return response.json()
