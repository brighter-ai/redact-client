import os
from pathlib import Path

import pytest

from redact.commons.utils import (
    files_in_dir,
    images_in_dir,
    normalize_path,
    parse_key_value_pairs,
)
from redact.utils import normalize_url


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


@pytest.mark.parametrize(
    "in_path, out_path",
    [
        ("./foo", str(Path(os.getcwd()).joinpath("foo"))),
    ],
)
def test_normalize_path(in_path: str, out_path: str):
    assert str(normalize_path(in_path)) == out_path


def test_files_in_dir(images_path: Path):
    # GIVEN a directory with images (ins subfolders)
    # WHEN the files are listed
    full_paths = files_in_dir(images_path, recursive=True, sort=True)
    relative_paths = [str(Path(p).relative_to(images_path)) for p in full_paths]
    # THEN all images and their subfolders are in the list
    assert relative_paths == [
        "sub_dir/img_0.jpeg",
        "sub_dir/img_1.jpeg",
        "sub_dir/img_2.jpeg",
    ]


def test_images_in_dir(images_path: Path):
    # GIVEN a directory with images (ins subfolders)
    # WHEN the files are listed
    full_paths = images_in_dir(images_path, recursive=True, sort=True)
    relative_paths = [str(Path(p).relative_to(images_path)) for p in full_paths]
    # THEN all images and their subfolders are in the list
    assert relative_paths == [
        "sub_dir/img_0.jpeg",
        "sub_dir/img_1.jpeg",
        "sub_dir/img_2.jpeg",
    ]


@pytest.mark.parametrize(
    "input, expected",
    [
        ([], {}),
        (["hello=world"], {"hello": "world"}),
        (["hello=wor=ld"], {"hello": "wor=ld"}),
        (["hello=world", "foo=boo"], {"hello": "world", "foo": "boo"}),
    ],
)
def test_parse_key_value_pairs(input, expected):
    parsed = parse_key_value_pairs(input)
    assert parsed == expected


@pytest.mark.parametrize(
    "input",
    [
        ["helloworld"],
        ["=world"],
        ["world="],
    ],
)
def test_parse_key_value_pairs_exception_on_illformatted(input):
    with pytest.raises(ValueError):
        _ = parse_key_value_pairs(input)
