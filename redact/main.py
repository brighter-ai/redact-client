import typer

from redact.api_versions import REDACT_API_VERSIONS
from redact.tools import v3, v4

HELP_TEXT = (
    "Default values are managed by the redact backend. "
    "For detailed information, please consult the "
    "official documentation at: "
    "https://docs.brighter.ai/reference/post_service-v%s-out-type"
)


def redact_file_entry_point():
    """Entry point for redact_file script as defined in 'pyproject.toml'."""
    app = typer.Typer()
    app.command(name=REDACT_API_VERSIONS.v3, help=HELP_TEXT % 3)(v3.redact_file)
    app.command(name=REDACT_API_VERSIONS.v4, help=HELP_TEXT % 4)(v4.redact_file)
    app(prog_name="redact_file")


def redact_folder_entry_point():
    """Entry point for redact_folder script as defined in 'pyproject.toml'."""
    app = typer.Typer()
    app.command(name=REDACT_API_VERSIONS.v3, help=HELP_TEXT % 3)(v3.redact_folder)
    app.command(name=REDACT_API_VERSIONS.v4, help=HELP_TEXT % 4)(v4.redact_folder)
    app(prog_name="redact_folder")
