"""Command Line Interface (CLI) entrypoint for complex-networks-laboratories."""

import typer

from complex_networks_laboratories import __version__
from complex_networks_laboratories.graph.loader import load_graph

app = typer.Typer(
    name="complex-networks",
    help="CLI tool for complex network analysis.",
)


@app.command()
def version() -> None:
    """Print the current application version."""
    typer.echo(f"complex-networks-laboratories version: {__version__}")


@app.command()
def info() -> None:
    """Display dataset and basic graph metrics."""
    try:
        graph = load_graph()
        nodes_count = graph.number_of_nodes()
        edges_count = graph.number_of_edges()
        typer.echo("=== Complex Networks Laboratories ===")
        typer.echo("Dataset: New Zealand Scientific Collaboration Network")
        typer.echo(f"Nodes: {nodes_count:,}")
        typer.echo(f"Edges: {edges_count:,}")
    except FileNotFoundError as err:
        typer.secho(f"Error loading graph: {err}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from err


if __name__ == "__main__":
    app()
