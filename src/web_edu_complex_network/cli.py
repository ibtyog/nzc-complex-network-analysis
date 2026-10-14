"""Command Line Interface (CLI) entrypoint for web-edu-complex-network."""

import typer

from web_edu_complex_network import __version__
from web_edu_complex_network.config import RAW_MTX_PATH

app = typer.Typer(
    name="web-edu",
    help="CLI tool for complex network analysis of the web-edu dataset.",
)


@app.command()
def version() -> None:
    """Print the current application version."""
    typer.echo(f"web-edu-complex-network version: {__version__}")


@app.command()
def info() -> None:
    """Display basic dataset and environment configuration information."""
    typer.echo("=== web-edu Complex Network ===")
    typer.echo(f"Raw MatrixMarket data path: {RAW_MTX_PATH}")
    exists = "Found" if RAW_MTX_PATH.exists() else "Missing"
    typer.echo(f"Raw data status: {exists}")


if __name__ == "__main__":
    app()
