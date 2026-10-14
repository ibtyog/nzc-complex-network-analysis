from web_edu_complex_network.config import RAW_MTX_PATH
from web_edu_complex_network.etl.silver import build_silver_tables, generate_edge_weights


def test_generate_edge_weights_constant() -> None:
    weights = generate_edge_weights(
        edge_count=10, mode="constant", seed=None, min_val=1.0, max_val=1.0
    )
    assert len(weights) == 10
    assert all(w == 1.0 for w in weights)


def test_generate_edge_weights_random_seeded() -> None:
    w1 = generate_edge_weights(edge_count=100, mode="random", seed=42, min_val=1.0, max_val=5.0)
    w2 = generate_edge_weights(edge_count=100, mode="random", seed=42, min_val=1.0, max_val=5.0)
    assert len(w1) == 100
    assert w1 == w2
    assert all(1.0 <= w <= 5.0 for w in w1)


def test_build_silver_tables_shapes() -> None:
    nodes, edges = build_silver_tables(RAW_MTX_PATH, weight_mode="constant", seed=None)
    assert len(nodes) == 3031
    assert len(edges) == 6474
    # Check node attributes
    first_node = nodes[0]
    assert first_node["node_id"] == 1
    assert first_node["name"] == "page_1"
    assert isinstance(first_node["degree"], int)
    assert isinstance(first_node["is_even_degree"], bool)
    assert first_node["is_even_degree"] == (first_node["degree"] % 2 == 0)
    # Check edge attributes
    first_edge = edges[0]
    assert "source" in first_edge and "target" in first_edge
    assert first_edge["weight"] == 1.0
    assert first_edge["capacity"] == 1.0
