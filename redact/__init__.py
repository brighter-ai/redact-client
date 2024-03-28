"""
Python client for "brighter Redact"
"""

__version__ = "8.1.0"

from .errors import RedactConnectError, RedactResponseError
from .v4.data_models import (
    InputType,
    JobArguments,
    JobPostResponse,
    JobResult,
    JobState,
    JobStatus,
    OutputType,
    Region,
    ServiceType,
)
from .v4.redact_instance import RedactInstance
from .v4.redact_job import RedactJob
from .v4.redact_requests import RedactRequests
from .v4.tools.redact_file import redact_file
from .v4.tools.redact_folder import redact_folder

__all__ = [
    redact_file,
    redact_folder,
    InputType,
    JobArguments,
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
