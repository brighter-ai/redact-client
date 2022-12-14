"""
Python client for "brighter Redact"
"""

__version__ = "6.0.0"

from .errors import RedactConnectError, RedactResponseError
from .v3.tools.redact_file import redact_file
from .v3.tools.redact_folder import redact_folder
from .v3.data_models import (
    InputType,
    JobArguments,
    JobLabels,
    JobPostResponse,
    JobResult,
    JobState,
    JobStatus,
    OutputType,
    Region,
    ServiceType,
)
from .v3.redact_instance import RedactInstance
from .v3.redact_job import RedactJob
from .v3.redact_requests import RedactRequests

__all__ = [
    redact_file,
    redact_folder,
    InputType,
    JobArguments,
    JobLabels,
    JobPostResponse,
    JobResult,
    JobState,
    JobStatus,
    OutputType,
    RedactConnectError,
    RedactResponseError,
    Region,
    ServiceType,
    RedactInstance,
    RedactJob,
    RedactRequests,
]
