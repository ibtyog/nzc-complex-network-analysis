"""Command Line Interface (CLI) entrypoint for complex-networks-laboratories."""

import networkx as nx
import typer

from complex_networks_laboratories import __version__
from complex_networks_laboratories.graph.loader import load_graph

app = typer.Typer(
    name="complex-networks",
    help="CLI tool for complex network analysis (Sieci Złożone).",
)


@app.command()
def version() -> None:
    """Print the current application version."""
    typer.echo(f"complex-networks-laboratories version: {__version__}")


@app.command()
def info() -> None:
    """Display dataset summary and key topological metrics."""
    try:
        graph = load_graph()
        nodes_count = graph.number_of_nodes()
        edges_count = graph.number_of_edges()
        density = nx.density(graph)

        components = list(nx.connected_components(graph))
        num_components = len(components)
        giant_size = max(len(c) for c in components)

        top_hubs = sorted(graph.nodes, key=lambda n: graph.degree[n], reverse=True)[:3]

        typer.echo("=== Complex Networks Laboratories ===")
        typer.echo("Dataset: New Zealand Scientific Collaboration Network")
        typer.echo(f"Nodes: {nodes_count:,}")
        typer.echo(f"Edges: {edges_count:,}")
        typer.echo(f"Density: {density:.6f}")
        typer.echo(f"Connected Components: {num_components}")
        typer.echo(f"Giant Component: {giant_size:,} nodes")
        typer.echo("\nTop Hub Institutions (by degree):")
        for rank, node_id in enumerate(top_hubs, start=1):
            name = graph.nodes[node_id]["name"]
            deg = graph.degree[node_id]
            typer.echo(f"  {rank}. {name} (degree: {deg})")
    except FileNotFoundError as err:
        typer.secho(f"Error loading graph: {err}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from err


if __name__ == "__main__":
    app()
