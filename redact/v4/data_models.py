import itertools
from json import JSONDecodeError
from typing import List, Optional
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Field, confloat, conint, validator
from strenum import StrEnum


class ServiceType(StrEnum):
    blur = "blur"
    dnat = "dnat"
    redact_area = "redact_area"
    mask = "mask"


class InputType(StrEnum):
    images = "images"
    videos = "videos"
    archives = "archives"


class OutputType(StrEnum):
    images = "images"
    videos = "videos"
    archives = "archives"
    overlays = "overlays"
    labels = "labels"


class Region(StrEnum):
    germany = "germany"
    mainland_china = "mainland_china"
    united_states_of_america = "united_states_of_america"
    japan = "japan"
    south_korea = "south_korea"

    def __str__(self):
        """Return 'germany' instead of 'Region.germany'. The latter is more helpful because the output
        is most likely to be used as a query parameter in an HTTP request."""
        return self.value


class JobArguments(BaseModel):
    region: Optional[Region] = None
    face: Optional[bool] = None
    license_plate: Optional[bool] = None
    full_body: Optional[bool] = None
    speed_optimized: Optional[bool] = None
    vehicle_recorded_data: Optional[bool] = None
    single_frame_optimized: Optional[bool] = None
    lp_determination_threshold: Optional[float] = Field(None, ge=0, le=1)
    face_determination_threshold: Optional[float] = Field(None, ge=0, le=1)
    full_body_segmentation_threshold: Optional[float] = Field(None, ge=0, le=1)
    status_webhook_url: Optional[AnyHttpUrl] = None
    areas_of_interest: Optional[List[List[int]]] = None

    @validator("areas_of_interest", pre=True)
    def _areas_of_interest(
        cls, value: Optional[List[str]]
    ) -> Optional[List[List[int]]]:
        if value is None or value == []:
            return None

        def validate_area(area: List[int]) -> List[int]:
            if len(area) != 4:
                raise ValueError

            if not (area[0] >= 0 and area[1] >= 0 and area[2] > 0 and area[3] > 0):
                raise ValueError

            return area

        def iou(area_0: List[int], area_1: List[int]) -> float:
            intersection_left = max(area_0[0], area_1[0])
            intersection_top = max(area_0[1], area_1[1])
            intersection_right = min(area_0[0] + area_0[2], area_1[0] + area_1[2])
            intersection_bottom = min(area_0[1] + area_0[3], area_1[1] + area_1[3])

            intersection_area = max(intersection_right - intersection_left, 0) * max(
                intersection_bottom - intersection_top, 0
            )
            union_area = (
                area_0[2] * area_0[3] + area_1[2] * area_1[3] - intersection_area
            )
            if union_area <= 0:
                return 0

            iou = intersection_area / union_area
            return iou

        def _validate_overlapping_areas(areas_of_interest: List[List[int]]) -> None:
            for area_0, area_1 in itertools.combinations(areas_of_interest, 2):
                if iou(area_0, area_1) > 0:
                    raise ValueError

        areas_of_interest = []
        try:
            for item in value:
                if len(item) == 0:
                    raise ValueError

                if isinstance(item, str):
                    item = [int(boundary) for boundary in item.split(",")]

                areas_of_interest.append(validate_area(item))

            _validate_overlapping_areas(areas_of_interest)

            return areas_of_interest

        except (JSONDecodeError, ValueError):
            raise ValueError(
                (
                    "Areas of interest must be a list of lists of 4 integers. "
                    "Coordinates of the left corner must be greater or equal to 0. "
                    "Height and width must be greater than 0. "
                    "Overlapping areas are not supported."
                )
            )


class JobPostResponse(BaseModel):
    output_id: UUID


class JobResult(BaseModel):
    content: bytes
    media_type: str
    file_name: str


class JobState(StrEnum):
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
    file_name: Optional[str] = None

    def is_running(self):
        return self.state in [JobState.active, JobState.pending]
