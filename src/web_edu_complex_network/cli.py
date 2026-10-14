"""Command Line Interface (CLI) entrypoint for web-edu-complex-network."""

from pathlib import Path
from typing import Annotated

import typer

from web_edu_complex_network import __version__
from web_edu_complex_network.config import DATA_SILVER_DIR, RAW_MTX_PATH
from web_edu_complex_network.etl.silver import run_silver_pipeline

app = typer.Typer(
    name="web-edu",
    help="CLI tool for complex network analysis of the web-edu dataset.",
)

etl_app = typer.Typer(
    name="etl",
    help="ETL pipeline commands for data layers (Bronze -> Silver -> Gold).",
)
app.add_typer(etl_app, name="etl")


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


@etl_app.command(name="silver")
def etl_silver(
    weight_mode: Annotated[
        str,
        typer.Option(
            "--weight-mode",
            "-m",
            help="Weight assignment mode: 'constant' or 'random'.",
        ),
    ] = "constant",
    seed: Annotated[
        int | None,
        typer.Option(
            "--seed",
            "-s",
            help="Optional random seed for reproducible random edge weights.",
        ),
    ] = None,
    min_weight: Annotated[
        float,
        typer.Option(
            "--min-weight",
            help="Minimum edge weight (must be > 0).",
        ),
    ] = 1.0,
    max_weight: Annotated[
        float,
        typer.Option(
            "--max-weight",
            help="Maximum edge weight (must be >= min-weight).",
        ),
    ] = 5.0,
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            "-o",
            help="Destination directory for generated nodes.csv and edges.csv.",
        ),
    ] = DATA_SILVER_DIR,
) -> None:
    """Transform Bronze MatrixMarket into Silver tabular datasets (nodes.csv & edges.csv)."""
    try:
        nodes_path, edges_path = run_silver_pipeline(
            raw_mtx_path=RAW_MTX_PATH,
            output_dir=output_dir,
            weight_mode=weight_mode,
            seed=seed,
            min_weight=min_weight,
            max_weight=max_weight,
        )
        typer.echo("Silver tables successfully created:")
        typer.echo(f"  - Nodes: {nodes_path}")
        typer.echo(f"  - Edges: {edges_path}")
    except (ValueError, FileNotFoundError) as err:
        typer.secho(f"Error executing silver ETL: {err}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from err


if __name__ == "__main__":
    app()
