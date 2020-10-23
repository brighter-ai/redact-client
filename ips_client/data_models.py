from enum import Enum
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ServiceType(str, Enum):
    blur = 'blur'
    dnat = 'dnat'


class OutputType(str, Enum):
    images = 'images'
    videos = 'videos'


class Region(str, Enum):

    european_union = 'european_union'
    mainland_china = 'mainland_china'
    united_states_of_america = 'united_states_of_america'

    def __str__(self):
        """Return 'european_union' instead of 'Region.european_union'. The latter is more helpful because the outpu
        is most likely to be used as a query parameter in an HTTP request."""
        return self.value


class JobArguments(BaseModel):
    region: Region = Region.european_union
    face: Optional[bool] = None
    license_plate: Optional[bool] = None
    person: Optional[bool] = None
    block_portraits: Optional[bool] = None
    speed_optimized: Optional[bool] = None


class JobPostResponse(BaseModel):
    output_id: UUID


class JobState(str, Enum):
    pending = 'pending'
    active = 'active'
    finished = 'completed'
    failed = 'failed'


class JobStatus(BaseModel):

    output_id: UUID
    state: JobState
    estimated_time_to_completion: Optional[float] = None

    def is_running(self):
        return self.state in [JobState.active, JobState.pending]
