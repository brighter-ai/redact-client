import time
from pathlib import Path
from uuid import UUID

from redact.settings import Settings
from redact.v3.data_models import (
    JobLabels,
    JobResult,
    JobStatus,
    OutputType,
    ServiceType,
)
from redact.v3.redact_requests import RedactRequests

settings = Settings()


class RedactJob:
    """
    RedactJob is intended to be the default, most convenient way for interacting with Redact. Use factory
    RedactInstance.start_job() to start new jobs.
    """

    def __init__(
        self,
        redact_requests: RedactRequests,
        service: ServiceType,
        out_type: OutputType,
        output_id: UUID,
    ):
        """
        Intended for internal use. Start a job through RedactInstance.start_job() instead.
        """
        self.redact = redact_requests
        self.service = service
        self.out_type = out_type
        self.output_id: UUID = output_id

    def get_status(self) -> JobStatus:
        response_dict = self.redact.get_status(
            service=self.service, out_type=self.out_type, output_id=self.output_id
        )
        return JobStatus(**response_dict)

    def get_labels(self, timeout: float = 60.0) -> JobLabels:
        return self.redact.get_labels(
            service=self.service,
            out_type=self.out_type,
            output_id=self.output_id,
            timeout=timeout,
        )

    def download_result(self, ignore_warnings: bool = False) -> JobResult:
        return self.redact.get_output(
            service=self.service,
            out_type=self.out_type,
            output_id=self.output_id,
            ignore_warnings=ignore_warnings,
        )

    def download_result_to_file(self, file: Path, ignore_warnings: bool = False):
        self.redact.write_output_to_file(
            service=self.service,
            out_type=self.out_type,
            output_id=self.output_id,
            file=file,
            ignore_warnings=ignore_warnings,
        )

    def delete(self):
        return self.redact.delete_output(
            service=self.service, out_type=self.out_type, output_id=self.output_id
        )

    def get_error(self):
        # TODO: Write test for this endpoint
        return self.redact.get_error(
            service=self.service, out_type=self.out_type, output_id=self.output_id
        )

    def wait_until_finished(self, sleep: float = 0.5) -> "RedactJob":
        while self.get_status().is_running():
            time.sleep(sleep)
        return self
