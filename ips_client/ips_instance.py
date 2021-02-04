from typing import Optional, IO

from ips_client.data_models import ServiceType, OutputType, JobArguments
from ips_client.ips_requests import IPSRequests
from ips_client.job import IPSJob
from ips_client.settings import Settings


settings = Settings()


class IPSInstance:

    def __init__(self, service: ServiceType, out_type: OutputType, ips_url: str = settings.ips_url_default):
        self.service = service
        self.out_type = out_type
        self.ips_requests = IPSRequests(ips_url=ips_url)

    def start_job(self, file: IO, job_args: Optional[JobArguments] = None) -> IPSJob:

        post_response = self.ips_requests.post_job(file=file,
                                                   service=self.service,
                                                   out_type=self.out_type,
                                                   job_args=job_args)

        return IPSJob(ips_requests=self.ips_requests,
                      service=self.service,
                      out_type=self.out_type,
                      output_id=post_response.output_id)
