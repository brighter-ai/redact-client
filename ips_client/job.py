import time

from copy import copy
from typing import IO
from uuid import UUID

from ips_client.data_models import ServiceType, OutputType, JobArguments, JobStatus, JobResult, JobLabels
from ips_client.ips_requests import IPSRequests
from ips_client.settings import Settings


settings = Settings()


class IPSJob:

    def __init__(self, ips_requests: IPSRequests, file: IO, service: ServiceType, out_type: OutputType, output_id: UUID,
                 job_args: JobArguments = JobArguments()):
        """Intended for internal use. Start a job through IPSInstance.start_job() instead."""
        self.ips = ips_requests
        self.service = service
        self.out_type = out_type
        self.output_id: UUID = output_id

    def get_status(self) -> JobStatus:
        response_dict = self.ips.get_status(service=self.service,
                                            out_type=self.out_type,
                                            output_id=self.output_id)
        return JobStatus(**response_dict)

    def get_labels(self) -> JobLabels:
        response_dict = self.ips.get_labels(service=self.service,
                                            out_type=self.out_type,
                                            output_id=self.output_id)
        return JobLabels(**response_dict)

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
