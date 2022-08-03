"""
Python client for "brighter Redact"
"""

__version__ = "4.8.0"

from .redact_instance import RedactInstance  # noqa
from .redact_job import RedactJob  # noqa
from .redact_requests import RedactRequests  # noqa

from .data_models import (  # noqa
    JobArguments,
    ServiceType,
    OutputType,
    Region,
    JobStatus,
    JobResult,
    JobLabels,
    JobState,
    JobPostResponse,
    RedactResponseError,
)

from .tools.redact_file import redact_file  # noqa
from .tools.redact_folder import redact_folder  # noqa
