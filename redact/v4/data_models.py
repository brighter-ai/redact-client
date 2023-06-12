import itertools
import json
from json import JSONDecodeError
from typing import List, Optional
from uuid import UUID

import numpy as np
from pydantic import AnyHttpUrl, BaseModel, Field, confloat, conint, root_validator, validator
from strenum import StrEnum


class ServiceType(StrEnum):
    blur = "blur"
    dnat = "dnat"
    extract = "extract"
    redact_area = "redact_area"


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


class AreaOfInterest(BaseModel):
    x: int
    y: int
    width: int
    height: int

    @root_validator
    def _check_edges(cls, values):
        x, y, height, width = (
            values.get("x"),
            values.get("y"),
            values.get("width"),
            values.get("height"),
        )

        if not (x >= 0 and y >= 0 and height > 0 and width > 0):
            raise ValueError

        return values

    def overlaps_with(self, other: "AreaOfInterest") -> bool:
        return self.iou(other) > 0

    def iou(self, other: "AreaOfInterest") -> float:
        intersection_left = max(self.x, other.x)
        intersection_top = max(self.y, other.y)
        intersection_right = min(self.x + self.width, other.x + other.width)
        intersection_bottom = min(self.y + self.height, other.y + other.height)

        intersection_area = max(intersection_right - intersection_left, 0) * np.maximum(
            intersection_bottom - intersection_top, 0
        )
        union_area = (
            self.width * self.height + other.width * other.height - intersection_area
        )
        if union_area <= 0:
            return 0

        iou = intersection_area / union_area
        return iou


class JobArguments(BaseModel):
    region: Optional[Region] = None
    face: Optional[bool] = None
    license_plate: Optional[bool] = None
    speed_optimized: Optional[bool] = None
    vehicle_recorded_data: Optional[bool] = None
    single_frame_optimized: Optional[bool] = None
    lp_determination_threshold: Optional[float] = Field(None, ge=0, le=1)
    face_determination_threshold: Optional[float] = Field(None, ge=0, le=1)
    status_webhook_url: Optional[AnyHttpUrl] = None
    areas_of_interest: Optional[List[AreaOfInterest]] = None

    @validator("areas_of_interest", pre=True)
    def _areas_of_interest(cls, value: Optional[str]) -> Optional[List[AreaOfInterest]]:
        if value is None:
            return value

        def validate_area(area: List[int]) -> AreaOfInterest:
            if len(area) != 4:
                raise ValueError

            return AreaOfInterest(x=area[0], y=area[1], width=area[2], height=area[3])

        def _validate_overlapping_areas(areas_of_interest: List[AreaOfInterest]) -> None:
            for area_0, area_1 in itertools.combinations(areas_of_interest, 2):
                if area_0.overlaps_with(area_1):
                    raise ValueError

        areas_of_interest = []
        try:
            areas = json.loads(value)
            for item in areas:
                if not isinstance(item, list) or len(item) == 0:
                    raise ValueError

                if isinstance(item[0], list):
                    for area in item:
                        areas_of_interest.append(validate_area(area))

                else:
                    areas_of_interest.append(validate_area(item))

            _validate_overlapping_areas(areas_of_interest)

            return areas_of_interest
        except (JSONDecodeError, ValueError) as e:
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
