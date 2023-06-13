from typing import Any, List

import pytest
from pydantic import ValidationError

from redact.v4 import JobArguments, Region


class TestJobArguments:
    @pytest.mark.parametrize(
        "areas_of_interest",
        [
            [[0, 0, 960, 540]],
            [
                [0, 0, 960, 540],
                [960, 0, 960, 540],
                [0, 540, 960, 540],
                [960, 540, 960, 540],
            ],
            ["0, 0, 960, 540"],
            ["0, 0, 960, 540", "960, 0, 960, 540"],
        ],
    )
    def test_job_arguments_with_areas_of_interest(self, areas_of_interest: List[Any]):
        job_args = JobArguments(
            region=Region.germany, areas_of_interest=areas_of_interest
        )

        for area in job_args.areas_of_interest:
            assert len(area) == 4
            for item in area:
                assert isinstance(item, int)

    @pytest.mark.parametrize(
        "areas_of_interest",
        [
            [[0, 0, 0, 960, 540]],
            [
                [0, 0, 960, "540"],
                [960, 0, 960, 540],
                [0, 540, 960, 540],
                [960, 540, 960, 540],
            ],
            ["0, 0, 960, 0, 540"],
            ["0, 0, 960, '540'", "960, 0, 960, 540"],
        ],
    )
    def test_job_arguments_fails_with_areas_of_interest(
        self, areas_of_interest: List[Any]
    ):
        with pytest.raises(ValidationError):
            JobArguments(region=Region.germany, areas_of_interest=areas_of_interest)
