from pathlib import Path

import networkx as nx
import pytest

from complex_networks_laboratories.graph.loader import load_graph


def test_load_graph_topology() -> None:
    G = load_graph()
    assert isinstance(G, nx.Graph)
    assert not G.is_directed()
    assert G.number_of_nodes() == 1511
    assert G.number_of_edges() == 4273
    assert nx.number_of_selfloops(G) == 0


def test_load_graph_attributes() -> None:
    G = load_graph()
    # Check node attributes
    node_0 = G.nodes[0]
    assert node_0["name"] == "TS-dot Engineering Ltd."
    # Check edge attributes
    assert G.has_edge(0, 518)
    assert G[0][518]["weight"] == 2
    # Verify weights are strictly positive integers
    assert all(isinstance(d["weight"], int) and d["weight"] > 0 for _, _, d in G.edges(data=True))


def test_load_graph_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_graph(nodes_path=tmp_path / "missing_nodes.csv")
