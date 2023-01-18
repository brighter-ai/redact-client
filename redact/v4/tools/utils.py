from pathlib import Path

from redact.v4 import OutputType
from redact.commons.utils import (
    is_image,
)


def get_file_extension(input_file_path: Path, output_type: OutputType) -> str:
    file_extension = input_file_path.suffix
    if output_type == OutputType.labels:
        file_extension = ".json"
    elif output_type == OutputType.overlays and not is_image(input_file_path):
        file_extension = ".apng"
    return file_extension
