"""Silver layer ETL module: transforms bronze MatrixMarket into tabular node and edge datasets."""

import random
from pathlib import Path
from typing import Any

import networkx as nx
import scipy.io as sio


def generate_edge_weights(
    edge_count: int,
    mode: str = "constant",
    seed: int | None = None,
    min_val: float = 1.0,
    max_val: float = 1.0,
) -> list[float]:
    """Generate weights for edges based on constant or random mode.

    Args:
        edge_count: Number of edges to generate weights for.
        mode: Weight generation mode, either 'constant' or 'random'.
        seed: Random seed for deterministic generation in 'random' mode.
        min_val: Minimum weight value (must be > 0).
        max_val: Maximum weight value (must be >= min_val).

    Returns:
        A list of float weights.

    Raises:
        ValueError: If mode is unsupported or weight range parameters are invalid.
    """
    if min_val <= 0:
        raise ValueError(f"Weight values must be strictly positive, got min_val={min_val}")
    if max_val < min_val:
        raise ValueError(f"max_val ({max_val}) cannot be smaller than min_val ({min_val})")

    if mode == "constant":
        return [float(min_val)] * edge_count
    elif mode == "random":
        rng = random.Random(seed)
        return [round(rng.uniform(min_val, max_val), 4) for _ in range(edge_count)]
    else:
        raise ValueError(
            f"Unsupported weight_mode '{mode}'. Supported modes: 'constant', 'random'."
        )


def build_silver_tables(
    mtx_path: Path,
    weight_mode: str = "constant",
    seed: int | None = None,
    min_weight: float = 1.0,
    max_weight: float = 5.0,
    default_capacity: float = 1.0,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Parse raw MatrixMarket file and build node and edge attribute dictionaries.

    Args:
        mtx_path: Path to the raw .mtx file.
        weight_mode: 'constant' or 'random'.
        seed: Random seed if weight_mode is 'random'.
        min_weight: Minimum weight value.
        max_weight: Maximum weight value.
        default_capacity: Default capacity attribute value on edges for max flow.

    Returns:
        Tuple of (nodes_records, edges_records).
    """
    if not mtx_path.is_file():
        raise FileNotFoundError(f"MatrixMarket file not found: {mtx_path}")

    # Read coordinate matrix (spmatrix=False avoids future deprecation warnings)
    adj_array = sio.mmread(mtx_path, spmatrix=False)
    raw_graph = nx.from_scipy_sparse_array(adj_array)

    # Relabel nodes to 1-based indexing matching original MatrixMarket coordinates
    graph = nx.relabel_nodes(raw_graph, lambda x: x + 1)

    # Build node records (sorted by node_id)
    nodes: list[dict[str, Any]] = []
    for node_id in sorted(graph.nodes()):
        degree = int(graph.degree[node_id])
        nodes.append(
            {
                "node_id": node_id,
                "name": f"page_{node_id}",
                "degree": degree,
                "is_even_degree": (degree % 2 == 0),
            }
        )

    # Extract deduplicated edges
    raw_edges = sorted(graph.edges())
    weights = generate_edge_weights(
        edge_count=len(raw_edges),
        mode=weight_mode,
        seed=seed,
        min_val=min_weight,
        max_val=max_weight,
    )

    # Build edge records
    edges: list[dict[str, Any]] = []
    for idx, (source, target) in enumerate(raw_edges):
        edges.append(
            {
                "source": source,
                "target": target,
                "weight": weights[idx],
                "capacity": default_capacity,
            }
        )

    return nodes, edges
