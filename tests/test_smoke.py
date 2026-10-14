"""Smoke tests to verify project setup, packaging, and configuration."""

from typer.testing import CliRunner

import complex_networks_laboratories
from complex_networks_laboratories.cli import app
from complex_networks_laboratories.config import EDGES_CSV_PATH, NODES_CSV_PATH

runner = CliRunner()


def test_package_import_and_version() -> None:
    """Verify package imports correctly and exposes a valid version string."""
    assert complex_networks_laboratories.__version__ == "0.1.0"


def test_dataset_files_exist() -> None:
    """Verify that the dataset CSV files exist at expected paths."""
    assert NODES_CSV_PATH.is_file(), f"Nodes CSV not found at {NODES_CSV_PATH}"
    assert EDGES_CSV_PATH.is_file(), f"Edges CSV not found at {EDGES_CSV_PATH}"


def test_cli_version_command() -> None:
    """Verify CLI version command runs successfully and reports the new name."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "complex-networks-laboratories version: 0.1.0" in result.stdout


def test_cli_info_command() -> None:
    """Verify CLI info command outputs dataset path information and graph metrics."""
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "New Zealand Scientific Collaboration Network" in result.stdout
    assert "Nodes: 1,511" in result.stdout
    assert "Edges: 4,273" in result.stdout
    assert "Connected Components: 24" in result.stdout
    assert "Giant Component: 1,463 nodes" in result.stdout
    assert "University of Auckland" in result.stdout
