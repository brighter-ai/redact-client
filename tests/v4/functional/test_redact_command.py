from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from redact.settings import Settings
from redact.tools.v4 import redact_file, redact_folder
from redact.v4 import InputType, JobArguments, OutputType, ServiceType


class TestRedactCommand:
    @pytest.fixture
    def redact_file_app(self):
        app = typer.Typer()
        app.command()(redact_file)
        return app

    @pytest.fixture
    def redact_folder_app(self):
        app = typer.Typer()
        app.command()(redact_folder)
        return app

    def test_redact_file_command_sends_none_values(
        self, images_path: Path, tmp_path_factory, mocker, redact_file_app
    ):
        output_path = tmp_path_factory.mktemp("imgs_dir_out")

        redact_file_mock = mocker.patch(
            "redact.tools.v4.rdct_file",
        )
        runner = CliRunner()
        result = runner.invoke(
            redact_file_app,
            [
                "--file-path",
                images_path,
                "--output-type",
                OutputType.images,
                "--service",
                ServiceType.blur,
                "--output-path",
                output_path,
            ],
        )

        assert result.exit_code == 0
        redact_file_mock.assert_called_once()
        redact_file_mock.assert_called_with(
            file_path=str(images_path),
            output_type=OutputType.images,
            service=ServiceType.blur,
            job_args=JobArguments(),
            licence_plate_custom_stamp_path=None,
            redact_url=Settings().redact_online_url,
            api_key=None,
            output_path=str(output_path),
            ignore_warnings=False,
            skip_existing=True,
            auto_delete_job=True,
        )

    def test_redact_folder_command_sends_none_values(
        self, images_path: Path, tmp_path_factory, mocker, redact_folder_app
    ):
        output_path = tmp_path_factory.mktemp("imgs_dir_out")

        redact_folder_mock = mocker.patch(
            "redact.tools.v4.rdct_folder",
        )
        runner = CliRunner()
        result = runner.invoke(
            redact_folder_app,
            [
                "--input-dir",
                images_path,
                "--output-type",
                OutputType.images,
                "--input-type",
                InputType.images,
                "--service",
                ServiceType.blur,
                "--output-dir",
                output_path,
            ],
        )

        assert result.exit_code == 0
        redact_folder_mock.assert_called_once()
        redact_folder_mock.assert_called_with(
            input_dir=str(images_path),
            output_dir=str(output_path),
            input_type=InputType.images,
            output_type=OutputType.images,
            service=ServiceType.blur,
            job_args=JobArguments(),
            licence_plate_custom_stamp_path=None,
            redact_url=Settings().redact_online_url,
            api_key=None,
            n_parallel_jobs=1,
            ignore_warnings=False,
            skip_existing=True,
            auto_delete_job=True,
            auto_delete_input_file=False,
        )
