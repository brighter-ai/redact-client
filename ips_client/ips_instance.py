from typing import Optional, IO, Union

from ips_client.data_models import ServiceType, OutputType, JobArguments, JobLabels
from ips_client.ips_requests import IPSRequests
from ips_client.job import IPSJob
from ips_client.settings import Settings


settings = Settings()


class IPSInstance:
    """
    Helper for starting new IPS jobs.
    """

    def __init__(self, ips_requests: IPSRequests, service: ServiceType, out_type: OutputType):
        """
        The default way for creating IPSInstance objects is through IPSInstance.create().
        """
        self.ips_requests = ips_requests
        self.service = service
        self.out_type = out_type

    @classmethod
    def create(cls, service: ServiceType, out_type: OutputType, ips_url: str = settings.ips_url_default,
               subscription_key: Optional[str] = None) -> 'IPSInstance':
        """
        The default way of creating IPSInstance objects.
        """
        ips_requests = IPSRequests(ips_url=ips_url, subscription_key=subscription_key)
        return cls(ips_requests=ips_requests, service=service, out_type=out_type)

    def start_job(self, file: IO, job_args: Optional[JobArguments] = None,
                  licence_plate_custom_stamp: Optional[IO] = None,
                  custom_labels: Optional[Union[str, IO, JobLabels]] = None) -> IPSJob:

        post_response = self.ips_requests.post_job(file=file,
                                                   service=self.service,
                                                   out_type=self.out_type,
                                                   job_args=job_args,
                                                   licence_plate_custom_stamp=licence_plate_custom_stamp,
                                                   custom_labels=custom_labels)

        return IPSJob(ips_requests=self.ips_requests,
                      service=self.service,
                      out_type=self.out_type,
                      output_id=post_response.output_id)
