"""Smoke tests to verify project setup, packaging, and configuration."""

from typer.testing import CliRunner

import web_edu_complex_network
from web_edu_complex_network.cli import app
from web_edu_complex_network.config import DATA_BRONZE_DIR, RAW_MTX_PATH

runner = CliRunner()


def test_package_import_and_version() -> None:
    """Verify package imports correctly and exposes a valid version string."""
    assert web_edu_complex_network.__version__ == "0.1.0"


def test_bronze_dataset_exists() -> None:
    """Verify that the bronze raw MatrixMarket file exists at the expected path."""
    assert DATA_BRONZE_DIR.is_dir(), f"Bronze directory not found at {DATA_BRONZE_DIR}"
    assert RAW_MTX_PATH.is_file(), f"Raw dataset not found at {RAW_MTX_PATH}"


def test_cli_version_command() -> None:
    """Verify CLI version command runs successfully."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_cli_info_command() -> None:
    """Verify CLI info command outputs dataset path information."""
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "Found" in result.stdout
