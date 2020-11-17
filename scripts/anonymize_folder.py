import typer

from ips_client.tools.anonymize_folder import anonymize_folder


app = typer.Typer()


if __name__ == '__main__':
    # programmatically decorate function with @app.command
    app.command()(anonymize_folder)
    app()
