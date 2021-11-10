from enum import Enum
from httpx import Response
from pydantic import BaseModel, Field, PositiveInt
from typing import Optional, List, Tuple
from uuid import UUID


class ServiceType(str, Enum):
    blur = 'blur'
    dnat = 'dnat'
    extract = 'extract'


class OutputType(str, Enum):
    images = 'images'
    videos = 'videos'
    archives = 'archives'
    overlays = 'overlays'


class Region(str, Enum):

    european_union = 'european_union'
    mainland_china = 'mainland_china'
    united_states_of_america = 'united_states_of_america'

    def __str__(self):
        """Return 'european_union' instead of 'Region.european_union'. The latter is more helpful because the output
        is most likely to be used as a query parameter in an HTTP request."""
        return self.value


class JobArguments(BaseModel):
    region: Region = Region.european_union
    face: Optional[bool] = None
    license_plate: Optional[bool] = None
    speed_optimized: Optional[bool] = None
    vehicle_recorded_data: Optional[bool] = None
    single_frame_optimized: Optional[bool] = None
    lp_determination_threshold: Optional[float] = Field(None, ge=0, le=1)
    face_determination_threshold: Optional[float] = Field(None, ge=0, le=1)


class JobPostResponse(BaseModel):
    output_id: UUID
    JobArguments


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
    start_timestamp: Optional[float] = None
    end_timestamp: Optional[float] = None
    estimated_time_to_completion: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)

    def is_running(self):
        return self.state in [JobState.active, JobState.pending]


class Label(BaseModel):
    bounding_box: Tuple[int, int, int, int]
    identity: int = 0
    score: Optional[float] = None


class LabelType(str, Enum):
    face: str = 'face'
    license_plate: str = 'license_plate'


class FrameLabels(BaseModel):
    index: PositiveInt
    faces: List[Label] = Field(default_factory=list)
    license_plates: List[Label] = Field(default_factory=list)

    def append(self, label: Label, label_type: LabelType):
        label_type = LabelType(label_type)
        if LabelType(label_type) == LabelType.face:
            self.faces.append(label)
        elif LabelType(label_type) == LabelType.license_plate:
            self.license_plates.append(label)
        else:
            raise ValueError()


class JobLabels(BaseModel):
    frames: List[FrameLabels]


class RedactConnectError(Exception):

    def __init__(self, msg: Optional[str] = None):
        super(RedactConnectError, self).__init__()
        self.msg = msg

    def __str__(self):
        return self.msg


class RedactResponseError(Exception):

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
