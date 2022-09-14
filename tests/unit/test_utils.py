import pytest

from redact.utils import (
    normalize_url,
    map_frame_data_to_new_label_format,
    bbox_to_corner_points,
    label_response_to_job_labels,
    store_corner_points_in_frame,
)
from redact.data_models import FrameLabels, JobLabels, Label
from typing import Dict, Any


@pytest.mark.parametrize(
    "input_url, output_url",
    [
        ("192.168.11.22", "http://192.168.11.22"),
        ("192.168.11.22:42", "http://192.168.11.22:42"),
        ("http://192.168.11.22", "http://192.168.11.22"),
        ("https://192.168.11.22", "https://192.168.11.22"),
        ("foo.org/bar", "http://foo.org/bar"),
        ("foo.org/bar/", "http://foo.org/bar/"),
    ],
)
def test_normalize_url(input_url: str, output_url: str):
    assert normalize_url(input_url) == output_url


def test_bbox_to_corner_points():
    bbox = [10, 40, 20, 50]
    corner_points = [
        (10, 40),
        (20, 40),
        (20, 50),
        (10, 50),
    ]
    assert corner_points == bbox_to_corner_points(bbox)


def get_frame_label(index: str, detection_type: str) -> FrameLabels:
    if detection_type == "no detection":
        return FrameLabels(index=index, redaction_areas=[])
    elif detection_type == "detection":
        return FrameLabels(
            index=index,
            redaction_areas=[Label(area=[(10, 40), (20, 40), (20, 50), (10, 50)])],
        )


def get_frame_response(index: str, detection_type: str) -> Dict[str, Any]:
    if detection_type == "no detection":
        return {"index": index, "faces": [], "license_plates": []}
    elif detection_type == "face":
        return {
            "index": index,
            "faces": [
                {
                    "bounding_box": [10, 40, 20, 50],
                    "identity": 0,
                    "score": 0.9,
                }
            ],
            "license_plates": [],
        }
    elif detection_type == "lp":
        return {
            "index": index,
            "faces": [
                {
                    "bounding_box": [10, 40, 20, 50],
                    "identity": 0,
                    "score": 0.9,
                }
            ],
            "license_plates": [],
        }


@pytest.mark.parametrize(
    "frame, expected_frame",
    [
        (get_frame_response("1", "no detection"), get_frame_label("1", "no detection")),
        (get_frame_response("1", "face"), get_frame_label("1", "detection")),
        (get_frame_response("1", "lp"), get_frame_label("1", "detection")),
    ],
)
def test_map_frame_data_to_new_label_format(
    frame: Dict[str, Any], expected_frame: FrameLabels
):
    assert expected_frame == map_frame_data_to_new_label_format(frame)


def get_frames_response(frame_count: str) -> Dict[str, Any]:
    if frame_count == "one_frame":
        return {"frames": [get_frame_response("1", "face")]}
    elif frame_count == "n_frames":
        return {
            "frames": [
                get_frame_response("1", "face"),
                get_frame_response("2", "no detection"),
                get_frame_response("3", "lp"),
            ]
        }


def get_job_label(frame_count: str) -> JobLabels:
    if frame_count == "one_frame":
        return JobLabels(frames=[get_frame_label("1", "detection")])
    elif frame_count == "n_frames":
        return JobLabels(
            frames=[
                get_frame_label("1", "detection"),
                get_frame_label("2", "no detection"),
                get_frame_label("3", "detection"),
            ]
        )


def test_store_corner_points_in_frame():
    area = [(10, 40), (20, 40), (20, 50), (10, 50)]
    frame = {
        "index": 1,
        "faces": [
            {
                "bounding_box": [10, 40, 20, 50],
                "identity": 0,
                "score": 0.9,
            }
        ],
        "license_plates": [],
    }
    expected_frame = {
        "index": 1,
        "faces": [
            {
                "bounding_box": [10, 40, 20, 50],
                "identity": 0,
                "score": 0.9,
            }
        ],
        "license_plates": [],
        "redaction_areas": [
            {
                "area": [
                    (10, 40),
                    (20, 40),
                    (20, 50),
                    (10, 50),
                ]
            }
        ],
    }
    store_corner_points_in_frame(area, frame)
    assert expected_frame == frame


@pytest.mark.parametrize(
    "frames, expected_frames_label",
    [
        (get_frames_response("one_frame"), get_job_label("one_frame")),
        (get_frames_response("n_frames"), get_job_label("n_frames")),
    ],
)
def test_label_response_to_job_labels(
    frames: Dict[str, Any], expected_frames_label: JobLabels
):
    assert expected_frames_label == label_response_to_job_labels(frames)
