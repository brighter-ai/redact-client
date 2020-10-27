import functools
import time

from copy import copy
from typing import Optional, IO
from uuid import UUID

from ips_client.data_models import ServiceType, OutputType, JobArguments, JobPostResponse, JobStatus, JobResult
from ips_client.ips_requests import IPSRequests
from ips_client.settings import Settings


settings = Settings()


class IPSJob:

    def __init__(self, file: IO, service: ServiceType, out_type: OutputType, output_id: UUID,
                 job_args: JobArguments = JobArguments(), ips_url: str = settings.ips_url_default):
        """Intended for internal use. Start a job through start_new() instead."""
        self.file = file
        self.service = service
        self.out_type = out_type
        self.output_id: UUID = output_id
        self.job_args = copy(job_args)
        self.ips = IPSRequests(ips_url=ips_url)

    @classmethod
    def start_new(cls, file: IO, service: ServiceType, out_type: OutputType, job_args: JobArguments = JobArguments(),
                  ips_url: str = settings.ips_url_default):

        ips = IPSRequests(ips_url=ips_url)
        post_response = ips.post_job(file=file,
                                     service=service,
                                     out_type=out_type,
                                     job_args=job_args)

        return cls(file=file,
                   service=service,
                   out_type=out_type,
                   job_args=job_args,
                   output_id=post_response.output_id,
                   ips_url=ips_url)

    def get_status(self) -> JobStatus:
        response_dict = self.ips.get_status(service=self.service,
                                            out_type=self.out_type,
                                            output_id=self.output_id)
        return JobStatus(**response_dict)

    def download_result(self) -> JobResult:
        return self.ips.get_output(service=self.service,
                                   out_type=self.out_type,
                                   output_id=self.output_id)

    def delete(self):
        return self.ips.delete_output(service=self.service,
                                      out_type=self.out_type,
                                      output_id=self.output_id)

    def get_error(self):
        # TODO: Write test for this endpoint
        return self.ips.get_error(service=self.service,
                                  out_type=self.out_type,
                                  output_id=self.output_id)

    def wait_until_finished(self, sleep: float = .5) -> 'IPSJob':
        while self.get_status().is_running():
            time.sleep(sleep)
        return self
