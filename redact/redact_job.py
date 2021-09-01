import time

from uuid import UUID

from redact.data_models import ServiceType, OutputType, JobStatus, JobResult, JobLabels
from redact.redact_requests import RedactRequests
from redact.settings import Settings


settings = Settings()


class RedactJob:
    """
    RedactJob is intended to be the default, most convenient way for interacting with Redact. Use factory
    RedactInstance.start_job() to start new jobs.
    """

    def __init__(self, redact_requests: RedactRequests, service: ServiceType, out_type: OutputType, output_id: UUID):
        """
        Intended for internal use. Start a job through RedactInstance.start_job() instead.
        """
        self.redact = redact_requests
        self.service = service
        self.out_type = out_type
        self.output_id: UUID = output_id

    def get_status(self) -> JobStatus:
        response_dict = self.redact.get_status(service=self.service,
                                               out_type=self.out_type,
                                               output_id=self.output_id)
        return JobStatus(**response_dict)

    def get_labels(self) -> JobLabels:
        labels = self.redact.get_labels(service=self.service,
                                        out_type=self.out_type,
                                        output_id=self.output_id)
        return labels

    def download_result(self) -> JobResult:
        return self.redact.get_output(service=self.service,
                                      out_type=self.out_type,
                                      output_id=self.output_id)

    def delete(self):
        return self.redact.delete_output(service=self.service,
                                         out_type=self.out_type,
                                         output_id=self.output_id)

    def get_error(self):
        # TODO: Write test for this endpoint
        return self.redact.get_error(service=self.service,
                                     out_type=self.out_type,
                                     output_id=self.output_id)

    def wait_until_finished(self, sleep: float = .5) -> 'RedactJob':
        while self.get_status().is_running():
            time.sleep(sleep)
        return self
