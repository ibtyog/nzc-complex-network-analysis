# web-edu-complex-network

Complex network analysis of the `web-edu` academic hyperlink dataset for the *Complex Networks* (Sieci Złożone) laboratory course.

---

## Project Overview

This repository hosts a modular Python project analyzing the topological properties and graph algorithms on the `web-edu` network.

* **Vertices (3,031):** Educational web pages and academic documents.
* **Edges (6,474):** Hyperlinks connecting pages.
* **System:** Information topology and hyperlink navigation across educational domains.

For a comprehensive domain description and citations, see [docs/dataset_description.md](docs/dataset_description.md).

---

## Architecture & Layout

```text
web-edu-complex-network/
├── pyproject.toml              # UV / packaging metadata, tool configs
├── tox.ini                     # Isolated test & lint environment runner
├── README.md                   # Project overview & developer guide
├── docs/
│   └── dataset_description.md  # Detailed academic description of the network
├── data/
│   ├── bronze/                 # Raw MatrixMarket source files (web-edu.mtx)
│   ├── silver/                 # Intermediate filtered edge tables
│   └── gold/                   # Enriched, analysis-ready graphs (GraphML)
├── notebooks/                  # Interactive Jupyter notebooks for laboratory tasks
├── tests/                      # Pytest test suite
└── src/
    └── web_edu_complex_network/
        ├── __init__.py
        ├── config.py           # Central filesystem paths & settings
        ├── etl/                # Bronze -> Silver -> Gold transformation pipelines
        ├── graph/              # Graph loading, models, and property computations
        ├── algorithms/         # Shortest path, Eulerian analysis, and Max Flow
        └── cli.py              # Interactive CLI application
```

---

## Quickstart

### Prerequisites
* Python `>= 3.11` (or Python `3.13`)
* [`uv`](https://github.com/astral-sh/uv) fast Python package manager

### Environment Setup
Install dependencies and configure virtual environment in editable mode:
```bash
uv sync
```

---

## Development Tools

### Running Tests
Execute smoke and unit tests with `pytest`:
```bash
uv run pytest
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

### Multi-Environment Testing with Tox
Run all checks in isolated virtual environments via `tox-uv`:
```bash
uv run tox
```

---

## CLI Usage

The project includes an interactive Command Line Interface:
```bash
uv run web-edu info
uv run web-edu version
```
