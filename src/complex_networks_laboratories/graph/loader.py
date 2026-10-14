"""Graph loader module for the New Zealand Scientific Collaboration Network."""

import csv
from pathlib import Path

import networkx as nx

from complex_networks_laboratories.config import EDGES_CSV_PATH, NODES_CSV_PATH


def load_graph(
    nodes_path: Path = NODES_CSV_PATH,
    edges_path: Path = EDGES_CSV_PATH,
) -> nx.Graph:
    """Load the scientific collaboration network into a typed NetworkX undirected graph.

    Args:
        nodes_path: Path to the raw CSV file containing node records.
        edges_path: Path to the raw CSV file containing edge records.

    Returns:
        nx.Graph: Undirected graph where nodes have 'name' (str) attribute
                  and edges have 'weight' (int) attribute.

    Raises:
        FileNotFoundError: If nodes_path or edges_path does not exist.
    """
    if not nodes_path.is_file():
        raise FileNotFoundError(f"Nodes file not found: {nodes_path}")
    if not edges_path.is_file():
        raise FileNotFoundError(f"Edges file not found: {edges_path}")

    graph: nx.Graph = nx.Graph()

    # Load node records (format: # index, _graphml_vertex_id, _pos)
    with open(nodes_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for row in reader:
            if not row:
                continue
            node_id = int(row[0])
            name = row[1]
            graph.add_node(node_id, name=name)

    # Load edge records (format: # source, target, _graphml_edge_id, weight)
    with open(edges_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for row in reader:
            if not row:
                continue
            u = int(row[0])
            v = int(row[1])
            weight = int(row[3])
            graph.add_edge(u, v, weight=weight)

    return graph
