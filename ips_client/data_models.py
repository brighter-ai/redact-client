from enum import Enum
from pydantic import BaseModel
from requests import Response
from typing import Optional, List
from uuid import UUID


class ServiceType(str, Enum):
    blur = 'blur'
    dnat = 'dnat'


class OutputType(str, Enum):
    images = 'images'
    videos = 'videos'
    archives = 'archives'


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


class JobResult(BaseModel):
    content: bytes
    media_type: str


class JobState(str, Enum):
    pending = 'pending'
    active = 'active'
    finished = 'completed'
    failed = 'failed'


class JobStatus(BaseModel):

    output_id: UUID
    state: JobState
    start_timestamp: Optional[float]
    end_timestamp: Optional[float]
    estimated_time_to_completion: Optional[float] = None
    start_timestamp: Optional[float] = None
    end_timestamp: Optional[float] = None

    def is_running(self):
        return self.state in [JobState.active, JobState.pending]


class JobLabels(BaseModel):
    # TODO Model the full data hierarchy
    faces: Optional[List]
    license_plates: Optional[List]
    frames: Optional[List]


class IPSResponseError(Exception):

    def __init__(self, response: Response, msg: Optional[str] = None):
        super().__init__()
        self.response: Response = response
        self.msg = msg

    @property
    def status_code(self) -> int:
        return self.response.status_code

    def __str__(self) -> str:
        s = str(self.response)
        if self.msg:
            s = s + ' ' + self.msg
        return s
