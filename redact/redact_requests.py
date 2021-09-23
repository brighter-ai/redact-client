import functools
import httpx
import logging
import urllib.parse

from io import FileIO
from typing import Dict, Optional, IO, Union
from uuid import UUID

from redact.data_models import (ServiceType, OutputType, JobArguments, JobResult, RedactResponseError, JobPostResponse,
                                JobLabels, RedactConnectError)
from redact.settings import Settings
from redact.utils import normalize_url

settings = Settings()

logging.basicConfig(level=settings.log_level.upper())
log = logging.getLogger('redact-requests')


def _reraise_custom_errors(func):
    """
    Decorator that translates connection errors (from httpx) to request's own error types.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except httpx.ConnectError as e:
            raise RedactConnectError(f'Error connecting to {args[0].redact_url}: {e}')
        except httpx.ConnectTimeout:
            raise RedactConnectError(f'Timeout connecting to {args[0].redact_url}')

    return wrapper


class RedactRequests:
    """
    Helper class wrapping requests to the Redact API.
    """

    API_VERSION = 'v3'

    def __init__(self, redact_url: str = settings.redact_url_default, subscription_id: Optional[str] = None,
                 api_key: Optional[str] = None):

        self.redact_url = normalize_url(redact_url)
        self.api_key = api_key
        self.subscription_id = subscription_id
        self._headers = {'Accept': '*/*'}

        if api_key:
            self._headers['api-key'] = self.api_key
        if subscription_id:
            self._headers['Subscription-Id'] = self.subscription_id

        self._client = httpx.Client(headers=self._headers)

    @_reraise_custom_errors
    def post_job(self, file: FileIO, service: ServiceType, out_type: OutputType,
                 job_args: Optional[JobArguments] = None, licence_plate_custom_stamp: Optional[IO] = None,
                 custom_labels: Optional[Union[str, IO, JobLabels]] = None) \
            -> JobPostResponse:
        """
        Post the job via a post request.
        """

        try:
            _ = file.name
        except AttributeError:
            raise ValueError("Expecting 'file' argument to have a 'name' attribute, i.e., FileIO.")

        url = urllib.parse.urljoin(self.redact_url, f'{service}/{self.API_VERSION}/{out_type}')

        if not job_args:
            job_args = JobArguments()

        files = {'file': file}
        if licence_plate_custom_stamp:
            files['licence_plate_custom_stamp'] = licence_plate_custom_stamp
        if custom_labels:
            files['custom_labels'] = custom_labels.json() if isinstance(custom_labels, JobLabels) else custom_labels

        with self._client as client:
            # TODO: Remove the timeout when Redact responds quicker after uploading large files
            response = client.post(url=url, files=files, params=job_args.dict(exclude_none=True), timeout=60)
        if response.status_code != 200:
            raise RedactResponseError(response=response, msg=f'Error posting job: {response.content}')

        return JobPostResponse(**response.json())

    @_reraise_custom_errors
    def get_output(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> JobResult:

        url = urllib.parse.urljoin(self.redact_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}')

        with self._client as client:
            response = client.get(url, timeout=60)

        if response.status_code != 200:
            raise RedactResponseError(response=response, msg='Error downloading job result')

        return JobResult(content=response.content,
                         media_type=response.headers['Content-Type'])

    @_reraise_custom_errors
    def get_status(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> Dict:

        url = urllib.parse.urljoin(self.redact_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}/status')

        with self._client as client:
            response = client.get(url, timeout=60)

        if response.status_code != 200:
            raise RedactResponseError(response=response, msg='Error getting job status')

        return response.json()

    @_reraise_custom_errors
    def get_labels(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> JobLabels:

        url = urllib.parse.urljoin(self.redact_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}/labels')

        with self._client as client:
            response = client.get(url, timeout=60)

        if response.status_code != 200:
            raise RedactResponseError(response=response, msg='Error getting labels')

        return JobLabels.parse_obj(response.json())

    @_reraise_custom_errors
    def delete_output(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> Dict:

        url = urllib.parse.urljoin(self.redact_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}')

        with self._client as client:
            response = client.delete(url, timeout=60)

        if response.status_code != 200:
            raise RedactResponseError(response=response, msg='Error deleting job')

        return response.json()

    @_reraise_custom_errors
    def get_error(self, service: ServiceType, out_type: OutputType, output_id: UUID) -> Dict:

        url = urllib.parse.urljoin(self.redact_url, f'{service}/{self.API_VERSION}/{out_type}/{output_id}/error')

        with self._client as client:
            response = client.get(url, timeout=60)

        if response.status_code != 200:
            raise RedactResponseError(response=response, msg='Error getting job error')

        return response.json()
