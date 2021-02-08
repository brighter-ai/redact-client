from typing import Optional, IO, Union

from ips_client.data_models import ServiceType, OutputType, JobArguments, JobLabels
from ips_client.ips_requests import IPSRequests
from ips_client.job import IPSJob
from ips_client.settings import Settings


settings = Settings()


class IPSInstance:
    """
    Factory for starting new IPS jobs.
    """

    def __init__(self, service: ServiceType, out_type: OutputType, ips_url: str = settings.ips_url_default,
                 subscription_key: Optional[str] = None):
        self.service = service
        self.out_type = out_type
        self.ips_requests = IPSRequests(ips_url=ips_url, subscription_key=subscription_key)

    def start_job(self, file: IO, job_args: Optional[JobArguments] = None,
                  custom_labels: Optional[Union[str, IO, JobLabels]] = None) -> IPSJob:

        post_response = self.ips_requests.post_job(file=file,
                                                   service=self.service,
                                                   out_type=self.out_type,
                                                   job_args=job_args,
                                                   custom_labels=custom_labels)

        return IPSJob(ips_requests=self.ips_requests,
                      service=self.service,
                      out_type=self.out_type,
                      output_id=post_response.output_id)
