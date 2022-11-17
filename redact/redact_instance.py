from typing import IO, BinaryIO, Optional, Union

from redact.data_models import JobArguments, JobLabels, OutputType, ServiceType
from redact.redact_job import RedactJob
from redact.redact_requests import RedactRequests
from redact.settings import Settings

settings = Settings()


class RedactInstance:
    """
    Helper for starting new Redact jobs.
    """

    def __init__(
        self,
        redact_requests: RedactRequests,
        service: ServiceType,
        out_type: OutputType,
    ):
        """
        The default way for creating RedactInstance objects is through RedactInstance.create().
        Here you can provide your own RedactRequests instance.
        """
        self.redact_requests = redact_requests
        self.service = service
        self.out_type = out_type

    @classmethod
    def create(
        cls,
        service: ServiceType,
        out_type: OutputType,
        redact_url: str = settings.redact_url_default,
        subscription_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> "RedactInstance":
        """
        The default way of creating RedactInstance objects.
        """
        redact_requests = RedactRequests(
            redact_url=redact_url, subscription_id=subscription_id, api_key=api_key
        )
        return cls(redact_requests=redact_requests, service=service, out_type=out_type)

    def start_job(
        self,
        file: BinaryIO,
        job_args: Optional[JobArguments] = None,
        licence_plate_custom_stamp: Optional[BinaryIO] = None,
        custom_labels: Optional[Union[str, IO, JobLabels]] = None,
    ) -> RedactJob:
        post_response = self.redact_requests.post_job(
            file=file,
            service=self.service,
            out_type=self.out_type,
            job_args=job_args,
            licence_plate_custom_stamp=licence_plate_custom_stamp,
            custom_labels=custom_labels,
        )
        return RedactJob(
            redact_requests=self.redact_requests,
            service=self.service,
            out_type=self.out_type,
            output_id=post_response.output_id,
        )
