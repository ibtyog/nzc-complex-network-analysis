# complex-networks-laboratories

Complex network analysis and graph algorithms for the *Complex Networks* (*Sieci Złożone*, Semester 5) course.

---

## Project Overview

This repository hosts a modular Python project implementing graph algorithms and structural analysis on the **New Zealand Scientific Collaborations (2010–2015)** network (`new_zealand_collab`).

* **Vertices (1,511):** Academic institutions, universities, Crown Research Institutes, hospitals, and industrial research laboratories across New Zealand.
* **Edges (4,273):** Joint scientific co-authorship relationships between researchers affiliated with pairs of institutions.
* **Edge Weights:** Integer count of joint publications indexed in Scopus (2010–2015), representing knowledge co-production and collaborative capacity.
* **System:** National scientific knowledge production, inter-institutional collaboration topology, and research collaboration dynamics.

For a comprehensive domain description, mathematical constraints, and formal citations, see [docs/dataset_description.md](docs/dataset_description.md).

---

## Architecture & Layout

```text
complex-networks-laboratories/
├── pyproject.toml              # UV / packaging metadata, tool configs
├── tox.ini                     # Isolated test & lint environment runner
├── README.md                   # Project overview & developer guide
├── docs/
│   └── dataset_description.md  # Detailed academic description of the network
├── data/
│   └── new_zealand_collab/     # Network CSV dataset from Netzschleuder
│       ├── nodes.csv           # Vertex catalog with institution names
│       ├── edges.csv           # Undirected co-authorship edges with Scopus weights
│       └── gprops.csv          # Dataset provenance and metadata
├── notebooks/                  # Interactive Jupyter notebooks for laboratory tasks
├── tests/                      # Pytest test suite
│   ├── test_smoke.py           # Smoke and CLI integration tests
│   └── graph/
│       └── test_loader.py      # Graph loader topology and invariant tests
└── src/
    └── complex_networks_laboratories/
        ├── __init__.py
        ├── config.py           # Central filesystem paths & settings
        ├── graph/              # In-memory graph loading and property models
        │   ├── __init__.py
        │   └── loader.py       # Zero-copy, direct NetworkX graph loader
        ├── algorithms/         # Shortest path, Eulerian analysis, and Max Flow
        └── cli.py              # Interactive CLI application
```

---

## Quickstart

### Prerequisites
* Python `>= 3.11` (tested with Python `3.13`)
* [`uv`](https://github.com/astral-sh/uv) fast Python package manager

### Environment Setup
Install dependencies and configure virtual environment in editable mode:
```bash
uv sync
```

---

## Development Tools

### Running Tests
Execute unit and integration tests with `pytest`:
```bash
uv run pytest
```

### Type Checking with Mypy
Verify strict type annotations:
```bash
uv run mypy src tests
```

### Linting & Formatting with Ruff
Check code quality:
```bash
uv run ruff check .
```

Format code:
```bash
uv run ruff format .
```

### Pyproject Formatting with pyproject-fmt
Validate and format `pyproject.toml`:
```bash
uv run pyproject-fmt --check pyproject.toml
```

### Multi-Environment Testing with Tox
Run all checks (`lint`, `format`, `mypy`, `pyproject-fmt`, `py313`) in isolated virtual environments via `tox-uv`:
```bash
uv run tox
```

---

## CLI Usage

The project includes an interactive Command Line Interface (`complex-networks`):

```bash
# Display version
uv run complex-networks version

# Inspect network metrics and hub institutions
uv run complex-networks info
```
