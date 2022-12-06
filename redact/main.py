import typer

from redact.settings import Settings
from redact.tools import v3

settings = Settings()


def redact_file_entry_point():
    """Entry point for redact_file script as defined in 'pyproject.toml'."""
    app = typer.Typer()
    app.command(name="v3")(v3.redact_file)
    app(prog_name="redact_file")


def redact_folder_entry_point():
    """Entry point for redact_folder script as defined in 'pyproject.toml'."""
    app = typer.Typer()
    app.command(name="v3")(v3.redact_folder)
    app(prog_name="redact_folder")
