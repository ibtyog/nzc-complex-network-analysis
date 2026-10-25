"""Graph loader module for the New Zealand Scientific Collaboration Network."""

import csv
from pathlib import Path

import networkx as nx
import numpy as np

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


def are_graphs_equal(g1: nx.Graph, g2: nx.Graph, check_weights: bool = False) -> bool:
    """Check if two undirected graphs have identical nodes and edges.

    Args:
        g1: First networkx graph.
        g2: Second networkx graph.
        check_weights: Whether to also verify that edge weights match.

    Returns:
        True if graphs have the same nodes and edges, False otherwise.
    """
    if set(g1.nodes) != set(g2.nodes):
        return False

    if check_weights:
        weighted_edges1 = {
            tuple(sorted((u, v))): data.get("weight") for u, v, data in g1.edges(data=True)
        }
        weighted_edges2 = {
            tuple(sorted((u, v))): data.get("weight") for u, v, data in g2.edges(data=True)
        }
        return weighted_edges1 == weighted_edges2

    unweighted_edges1 = {tuple(sorted((u, v))) for u, v in g1.edges()}
    unweighted_edges2 = {tuple(sorted((u, v))) for u, v in g2.edges()}
    return unweighted_edges1 == unweighted_edges2


def graph_from_incidence_matrix(incidence_matrix: np.ndarray) -> nx.Graph:
    """Reconstruct an undirected NetworkX graph from an incidence matrix.

    Args:
        incidence_matrix: 2D NumPy array of shape (|V|, |E|), where columns represent
                          edges and rows represent vertices (with 1 indicating incidence).

    Returns:
        nx.Graph: Reconstructed undirected graph containing all nodes and edges.
    """
    num_nodes, num_edges = incidence_matrix.shape
    graph: nx.Graph = nx.Graph()
    graph.add_nodes_from(range(num_nodes))

    # Retrieve row (vertex) and column (edge) indices of non-zero entries
    row_indices, col_indices = np.where(incidence_matrix != 0)

    # Group incident vertices by their edge column index
    edge_map: dict[int, list[int]] = {}
    for r, c in zip(row_indices, col_indices, strict=False):
        edge_map.setdefault(c, []).append(int(r))

    for endpoints in edge_map.values():
        if len(endpoints) == 2:
            graph.add_edge(endpoints[0], endpoints[1])
        elif len(endpoints) == 1:
            # Self-loop case, if present
            graph.add_edge(endpoints[0], endpoints[0])

    return graph
