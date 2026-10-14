"""Configuration and project path definitions."""

from pathlib import Path

# Base project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Dataset paths (New Zealand Scientific Collaboration Network)
DATASET_DIR = DATA_DIR / "new_zealand_collab"
NODES_CSV_PATH = DATASET_DIR / "nodes.csv"
EDGES_CSV_PATH = DATASET_DIR / "edges.csv"
GPROPS_CSV_PATH = DATASET_DIR / "gprops.csv"
