import functools
import requests
import time
import urllib.parse

from copy import copy
from enum import Enum
from pydantic import BaseModel
from typing import BinaryIO, Optional, Dict
from uuid import UUID

from ips_client.ips_data_models import IPSJobPostResponse, IPSJobStatus


# requests should always be used with a timeout to avoid hanging indefinitely:
# https://requests.readthedocs.io/en/master/user/quickstart/#timeouts
REQUESTS_TIMEOUT = 30


class ServiceType(str, Enum):
    blur = 'blur'
    dnat = 'dnat'


class OutputType(str, Enum):
    images = 'images'
    videos = 'videos'


class Region(str, Enum):
    european_union = 'european_union'
    mainland_china = 'mainland_china'
    united_states_of_america = 'united_states_of_america'


class JobArguments(BaseModel):
    service: ServiceType
    out_type: OutputType
    region: Region = Region.european_union
    face: Optional[bool] = None
    license_plate: Optional[bool] = None
    person: Optional[bool] = None
    block_portraits: Optional[bool] = None
    speed_optimized: Optional[bool] = None


def _require_job_started(func):
    """Decorator that throws an exception when a job does not have an output_id yet."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        job = args[0]
        if not job.output_id:
            raise RuntimeError(f'Job has no output_id. Did you start it?')
        return func(*args, **kwargs)
    return wrapper


class IPSJob:

    API_VERSION = 'v3'

    def __init__(self, file: BinaryIO, job_args: JobArguments, ips_url: str = 'http://127.0.0.1:8787/',
                 start_job: bool = True):

        self.file = file
        self.job_args = copy(job_args)
        self.ips_url = self._normalize_url(ips_url)

        self._post_response: Optional[IPSJobPostResponse] = None

        if start_job:
            self.start()

    def start(self) -> 'IPSJob':
        if not self.output_id:
            self._post_job()
        return self

    def _post_job(self) -> IPSJobPostResponse:
        """
        If not posted yet, post the job and store the response self._post_response.
        """

        if self.output_id:
            raise RuntimeError(f'Job has been posted before: output_id={self.output_id}')

        response_dict: dict = self._post_request()
        response = IPSJobPostResponse(**response_dict)

        self._post_response = response
        return response

    def _post_request(self) -> dict:
        """
        Post the job via a post request.
        """

        url = urllib.parse.urljoin(self.ips_url, f'/{self.job_args.service}/{self.API_VERSION}/{self.job_args.out_type}')
        files = {'file': self.file}

        response = requests.post(url=url,
                                 files=files,
                                 params=self._get_query_params(job_args=self.job_args),
                                 timeout=REQUESTS_TIMEOUT)

        if response.status_code != 200:
            raise RuntimeError(f'Error while posting job: {response}')

        return response.json()

    @staticmethod
    def _get_query_params(job_args: JobArguments) -> dict:
        """Returns those arguments that the IPS API expects as query parameters."""
        params = job_args.dict()
        # remove path parameters
        params.pop('service')
        params.pop('out_type')
        return params

    @property
    def output_id(self) -> Optional[UUID]:
        if self._post_response:
            return self._post_response.output_id
        return None

    def get_status(self) -> IPSJobStatus:
        response_dict = self._get_status_response()
        return IPSJobStatus(**response_dict)

    @_require_job_started
    def _get_status_response(self) -> dict:

        url = urllib.parse.urljoin(self.ips_url, f'/{self.job_args.service}/{self.API_VERSION}/{self.job_args.out_type}/{self.output_id}/status')
        response = requests.get(url, timeout=REQUESTS_TIMEOUT)

        if response.status_code != 200:
            raise RuntimeError(f'Error while getting job status: {response}')

        return response.json()

    def download_result(self) -> bytes:
        return self._get_result()

    @_require_job_started
    def _get_result(self) -> bytes:

        url = urllib.parse.urljoin(self.ips_url, f'/{self.job_args.service}/{self.API_VERSION}/{self.job_args.out_type}/{self.output_id}')
        response = requests.get(url, timeout=REQUESTS_TIMEOUT)

        if response.status_code != 200:
            raise RuntimeError(f'Error while getting job result: {response}')

        return response.content

    def delete(self):
        return self._delete()

    @_require_job_started
    def _delete(self) -> Dict:

        url = urllib.parse.urljoin(self.ips_url, f'/{self.job_args.service}/{self.API_VERSION}/{self.job_args.out_type}/{self.output_id}')
        response = requests.delete(url, timeout=REQUESTS_TIMEOUT)

        if response.status_code != 200:
            raise RuntimeError(f'Error while deleting job: {response}')

        return response.json()

    def get_error(self):
        return self._get_error()

    @_require_job_started
    def _get_error(self) -> Dict:

        url = urllib.parse.urljoin(self.ips_url, f'/{self.job_args.service}/{self.API_VERSION}/{self.job_args.out_type}/{self.output_id}/error')
        response = requests.delete(url, timeout=REQUESTS_TIMEOUT)

        if response.status_code != 200:
            raise RuntimeError(f'Error while getting job errors: {response}')

        return response.json()

    @_require_job_started
    def wait_until_finished(self, sleep: float = .5) -> 'IPSJob':
        while self.get_status().is_running():
            time.sleep(sleep)
        return self

    @staticmethod
    def _normalize_url(url: str):
        parse_result = urllib.parse.urlparse(url)
        if not parse_result.scheme:
            new_url = f'http://{url}'
            assert urllib.parse.urlparse(new_url).scheme == 'http'
            assert urllib.parse.urlparse(new_url).netloc == url, f'Error with URL: {new_url}'
            return new_url
        return url
