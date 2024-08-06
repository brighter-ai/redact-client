from typing import BinaryIO, Dict, Optional

from redact.settings import Settings
from redact.v4.data_models import JobArguments, OutputType, ServiceType
from redact.v4.redact_job import RedactJob
from redact.v4.redact_requests import RedactRequests

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
        custom_headers: Optional[Dict] = None,
        start_job_timeout: Optional[float] = 60.0,
    ) -> "RedactInstance":
        """
        The default way of creating RedactInstance objects.
        """
        redact_requests = RedactRequests(
            redact_url=redact_url,
            subscription_id=subscription_id,
            api_key=api_key,
            custom_headers=custom_headers,
            start_job_timeout=start_job_timeout,
        )
        return cls(redact_requests=redact_requests, service=service, out_type=out_type)

    def start_job(
        self,
        file: BinaryIO,
        job_args: Optional[JobArguments] = None,
        licence_plate_custom_stamp: Optional[BinaryIO] = None,
    ) -> RedactJob:
        post_response = self.redact_requests.post_job(
            file=file,
            service=self.service,
            out_type=self.out_type,
            job_args=job_args,
            licence_plate_custom_stamp=licence_plate_custom_stamp,
        )

        return RedactJob(
            redact_requests=self.redact_requests,
            service=self.service,
            out_type=self.out_type,
            output_id=post_response.output_id,
        )
