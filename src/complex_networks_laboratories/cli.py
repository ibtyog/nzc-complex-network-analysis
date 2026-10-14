"""Command Line Interface (CLI) entrypoint for complex-networks-laboratories."""

from pathlib import Path
from typing import Annotated

import typer

from complex_networks_laboratories import __version__
from complex_networks_laboratories.config import DATA_SILVER_DIR, RAW_MTX_PATH

app = typer.Typer(
    name="complex-networks",
    help="CLI tool for complex network analysis.",
)

etl_app = typer.Typer(
    name="etl",
    help="ETL pipeline commands for data layers (Bronze -> Silver -> Gold).",
)
app.add_typer(etl_app, name="etl")


@app.command()
def version() -> None:
    """Print the current application version."""
    typer.echo(f"complex-networks-laboratories version: {__version__}")


@app.command()
def info() -> None:
    """Display basic dataset and environment configuration information."""
    typer.echo("=== Complex Networks Laboratories ===")
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
    from complex_networks_laboratories.etl.silver import run_silver_pipeline

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
