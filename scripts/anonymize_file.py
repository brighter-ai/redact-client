import typer

from ips_client.tools.anonymize_file import anonymize_file


app = typer.Typer()


if __name__ == '__main__':
    # programmatically decorate function with @app.command
    app.command()(anonymize_file)
    app()
