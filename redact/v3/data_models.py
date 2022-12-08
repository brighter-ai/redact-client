from enum import Enum
from typing import List, Optional, Tuple
from uuid import UUID

from pydantic import BaseModel, Field, PositiveInt, confloat, conint


class ServiceType(str, Enum):
    blur = "blur"
    dnat = "dnat"
    extract = "extract"


class InputType(str, Enum):
    images = "images"
    videos = "videos"
    archives = "archives"


class OutputType(str, Enum):
    images = "images"
    videos = "videos"
    archives = "archives"
    overlays = "overlays"


class Region(str, Enum):

    european_union = "european_union"
    mainland_china = "mainland_china"
    united_states_of_america = "united_states_of_america"

    def __str__(self):
        """Return 'european_union' instead of 'Region.european_union'. The latter is more helpful because the output
        is most likely to be used as a query parameter in an HTTP request."""
        return self.value


class JobArguments(BaseModel):
    region: Optional[Region] = None
    face: Optional[bool] = None
    license_plate: Optional[bool] = None
    speed_optimized: Optional[bool] = None
    vehicle_recorded_data: Optional[bool] = None
    single_frame_optimized: Optional[bool] = None
    lp_determination_threshold: Optional[float] = Field(None, ge=0, le=1)
    face_determination_threshold: Optional[float] = Field(None, ge=0, le=1)


class JobPostResponse(BaseModel):
    output_id: UUID


class JobResult(BaseModel):
    content: bytes
    media_type: str


class JobState(str, Enum):
    pending = "pending"
    active = "active"
    finished = "completed"
    failed = "failed"


class JobStatus(BaseModel):

    output_id: UUID
    state: JobState
    start_timestamp: Optional[float] = None
    end_timestamp: Optional[float] = None
    estimated_time_to_completion: Optional[float] = None
    progress: Optional[confloat(ge=0.0, le=1.0)]
    total_frames: Optional[conint(ge=1)]
    warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None

    def is_running(self):
        return self.state in [JobState.active, JobState.pending]


class Label(BaseModel):
    bounding_box: Tuple[int, int, int, int]
    identity: int = 0
    score: Optional[float] = None


class LabelType(str, Enum):
    face: str = "face"
    license_plate: str = "license_plate"


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
