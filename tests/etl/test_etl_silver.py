import csv
from pathlib import Path

from complex_networks_laboratories.config import RAW_MTX_PATH
from complex_networks_laboratories.etl.silver import (
    build_silver_tables,
    generate_edge_weights,
    run_silver_pipeline,
    save_silver_tables,
)


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


def test_run_silver_pipeline_creates_files(tmp_path: Path) -> None:
    nodes_csv = tmp_path / "nodes.csv"
    edges_csv = tmp_path / "edges.csv"

    nodes, edges = build_silver_tables(RAW_MTX_PATH, weight_mode="constant", seed=None)
    save_silver_tables(nodes, edges, nodes_csv, edges_csv)

    assert nodes_csv.exists()
    assert edges_csv.exists()

    with open(nodes_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 3031
        assert rows[0]["name"] == "page_1"
        assert rows[0]["is_even_degree"] in ["True", "False"]

    with open(edges_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 6474
        assert float(rows[0]["weight"]) == 1.0
        assert float(rows[0]["capacity"]) == 1.0


def test_run_silver_pipeline_end_to_end(tmp_path: Path) -> None:
    nodes_path, edges_path = run_silver_pipeline(
        raw_mtx_path=RAW_MTX_PATH,
        output_dir=tmp_path,
        weight_mode="random",
        seed=123,
    )
    assert nodes_path.is_file()
    assert edges_path.is_file()


def test_cli_etl_silver_constant(tmp_path: Path) -> None:
    from typer.testing import CliRunner

    from complex_networks_laboratories.cli import app

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "etl",
            "silver",
            "--weight-mode",
            "constant",
            "--output-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert "Silver tables successfully created" in result.stdout
    assert (tmp_path / "nodes.csv").is_file()
    assert (tmp_path / "edges.csv").is_file()


def test_cli_etl_silver_invalid_mode() -> None:
    from typer.testing import CliRunner

    from complex_networks_laboratories.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["etl", "silver", "--weight-mode", "invalid_mode"])
    assert result.exit_code != 0
