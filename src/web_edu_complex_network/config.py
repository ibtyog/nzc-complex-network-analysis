"""Configuration and project path definitions."""

from pathlib import Path

# Base project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Medallion data layer paths
DATA_BRONZE_DIR = DATA_DIR / "bronze"
DATA_SILVER_DIR = DATA_DIR / "silver"
DATA_GOLD_DIR = DATA_DIR / "gold"

# Key dataset file paths
RAW_MTX_PATH = DATA_BRONZE_DIR / "web-edu.mtx"
SILVER_EDGES_CSV_PATH = DATA_SILVER_DIR / "edges.csv"
GOLD_GRAPHML_PATH = DATA_GOLD_DIR / "web_edu.graphml"
