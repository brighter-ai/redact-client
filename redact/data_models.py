import warnings

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

__all__ = [
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
]

warnings.warn(
    "Deprecated: Please import the data models from redact and not redact.data_models"
)
