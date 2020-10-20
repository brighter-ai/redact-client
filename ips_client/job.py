import functools
import time

from copy import copy
from io import BufferedIOBase
from typing import Optional
from uuid import UUID

from ips_client.data_models import ServiceType, OutputType, JobArguments, JobPostResponse, JobStatus
from ips_client.ips_api_wrapper import IPSApiWrapper


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

    def __init__(self, file: BufferedIOBase, service: ServiceType, out_type: OutputType,
                 job_args: JobArguments = JobArguments(), ips_url: str = 'http://127.0.0.1:8787/',
                 start_job: bool = True):

        self.file = file
        self.service = service
        self.out_type = out_type
        self.job_args = copy(job_args)
        self.ips = IPSApiWrapper(ips_url=ips_url)

        self.output_id: Optional[UUID] = None

        if start_job:
            self.start()

    def start(self) -> 'IPSJob':
        if not self.output_id:
            self._post_job()
        return self

    def _post_job(self) -> JobPostResponse:
        """
        If not posted yet, post the job and store the response self._post_response.
        """

        if self.output_id:
            raise RuntimeError(f'Job has been posted before: output_id={self.output_id}')

        response_dict: dict = self.ips.post_job(file=self.file,
                                                service=self.service,
                                                out_type=self.out_type,
                                                job_args=self.job_args)

        response = JobPostResponse(**response_dict)

        self.output_id = response.output_id
        return response

    @_require_job_started
    def get_status(self) -> JobStatus:
        response_dict = self.ips.get_status(service=self.service,
                                            out_type=self.out_type,
                                            output_id=self.output_id)
        return JobStatus(**response_dict)

    @_require_job_started
    def download_result(self) -> bytes:
        return self.ips.get_output(service=self.service,
                                   out_type=self.out_type,
                                   output_id=self.output_id)

    @_require_job_started
    def delete(self):
        return self.ips.delete_output(service=self.service,
                                      out_type=self.out_type,
                                      output_id=self.output_id)

    @_require_job_started
    def get_error(self):
        # TODO: Write test for this endpoint
        return self.ips.get_error(service=self.service,
                                  out_type=self.out_type,
                                  output_id=self.output_id)

    @_require_job_started
    def wait_until_finished(self, sleep: float = .5) -> 'IPSJob':
        while self.get_status().is_running():
            time.sleep(sleep)
        return self
