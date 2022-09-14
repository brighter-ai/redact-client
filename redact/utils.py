import urllib.parse

from typing import Any, Dict, List, Tuple
from redact.data_models import FrameLabels, JobLabels, Label
from pydantic import parse_obj_as


def normalize_url(url: str):
    parse_result = urllib.parse.urlparse(url)
    if not parse_result.scheme or not parse_result.netloc:
        new_url = f"http://{url}"
        if urllib.parse.urlparse(new_url).scheme != "http":
            raise ValueError()
        return new_url
    return url


def bbox_to_corner_points(bbox: List[int]) -> List[Tuple[int, int]]:
    area = [
        (bbox[0], bbox[1]),
        (bbox[2], bbox[1]),
        (bbox[2], bbox[3]),
        (bbox[0], bbox[3]),
    ]
    return area


def store_corner_points_in_frame(
    area: List[Tuple[int, int]], frame: Dict[str, Any]
) -> None:
    if "redaction_areas" in frame:
        frame["redaction_areas"].append({"area": area})
    else:
        frame["redaction_areas"] = [{"area": area}]


def parse_frame_to_label(frame: Dict[str, Any]) -> List[Label]:
    if "redaction_areas" not in frame:
        return []
    return [*parse_obj_as(List[Label], frame["redaction_areas"])]


def map_frame_data_to_new_label_format(frame: Dict[str, Any]) -> FrameLabels:
    [
        store_corner_points_in_frame(
            bbox_to_corner_points(bbox=bbox["bounding_box"]), frame
        )
        for bbox in [*frame["faces"], *frame["license_plates"]]
    ]
    detections = parse_frame_to_label(frame)
    return FrameLabels(
        index=frame["index"],
        redaction_areas=detections,
    )


def label_response_to_job_labels(label_response: Dict[str, Any]) -> JobLabels:
    frames = [
        map_frame_data_to_new_label_format(frame=f) for f in label_response["frames"]
    ]
    return JobLabels(frames=frames)
