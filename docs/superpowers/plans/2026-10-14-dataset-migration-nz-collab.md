# New Zealand Scientific Collaboration Network Setup & Direct Loader Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the project foundation for *Sieci Złożone* (Zadanie 1) using the `new_zealand_collab` dataset, replacing the initial `web-edu` attempt and completely eliminating the synthetic Medallion ETL layer in favor of direct, zero-copy graph loading into NetworkX.

**Architecture:** Data is stored directly as raw tabular CSV files in `data/new_zealand_collab/` (`nodes.csv`, `edges.csv`, `gprops.csv`). A single lightweight loader module (`graph/loader.py`) streams CSV records into a typed `networkx.Graph` in ~15 ms with node names and publication count edge weights. The CLI exposes `info` and `version` directly from the loaded graph model without requiring intermediate ETL execution.

**Tech Stack:** Python ≥3.11, uv, NetworkX, Typer, Pytest, Ruff, tox.

**Spec:**
- Source Dataset: New Zealand Scientific Collaboration Network (Netzschleuder / Scopus 2010–2015).
- Package Name: `complex_networks_laboratories` (dist name: `complex-networks-laboratories`, CLI: `complex-networks`).
- Graph Properties: Undirected, weighted, 1,511 nodes (institutions), 4,273 edges (co-authorship links, weights 1..1039).
- Architecture Decision: No Medallion ETL (no bronze/silver/gold directories, no `etl/` modules, no `etl` CLI commands).

## Global Constraints

- Code, docstrings, CLI output, and documentation in English.
- No synthetic data generation; no `scipy` dependency.
- Graph loader must return an undirected `networkx.Graph` with:
  - Node IDs: `int` (0-based `0..1510`).
  - Node attributes: `name` (`str`, institution name from column `_graphml_vertex_id`).
  - Edge attributes: `weight` (`int`, co-authorship count).
- Every task must leave the repo completely green: `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`.

## Review Focus

1. **Memory efficiency & fast loading:** `load_graph()` must load directly via standard library `csv` without reading extra unused columns (`_pos`, `_graphml_edge_id`).
2. **Missing data file handling:** Clear `FileNotFoundError` with meaningful message if CSVs are missing.
3. **Graph topology invariants:** Loaded graph must exactly match verified counts (1,511 nodes, 4,273 edges, 0 self-loops, 24 connected components).
4. **Clean codebase:** No leftover references to `web_edu`, `bronze`, `silver`, `gold`, `scipy`, or `etl`.
5. **CLI robustness:** `complex-networks info` gracefully reports summary statistics (nodes, edges, density, components, top-degree hubs) without requiring prior data transformation steps.

---

### Task 1: Rename package to `complex_networks_laboratories` & drop `scipy`

**Files:**
- Move: `src/web_edu_complex_network/` → `src/complex_networks_laboratories/` (`git mv`)
- Delete: `docs/superpowers/plans/2026-10-14-gold-layer-etl.md` (untracked file)
- Modify: `pyproject.toml` (`name`, dependencies without `scipy`, `[project.scripts]`, hatch package name, ruff isort)
- Modify: `src/complex_networks_laboratories/cli.py`, `src/complex_networks_laboratories/config.py`
- Modify: `tests/test_smoke.py`

**Interfaces:**
- Produces: Import root `complex_networks_laboratories`; CLI script `complex-networks`.

- [ ] **Step 1: Write failing smoke test** in `tests/test_smoke.py` asserting package name and version string:

```python
import complex_networks_laboratories
from typer.testing import CliRunner
from complex_networks_laboratories.cli import app

runner = CliRunner()


def test_package_import_and_version() -> None:
    assert complex_networks_laboratories.__version__ == "0.1.0"


def test_cli_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "complex-networks-laboratories version: 0.1.0" in result.stdout
```

- [ ] **Step 2: Run test to verify failure**
  Run: `uv run pytest tests/test_smoke.py`
  Expected: FAIL with `ModuleNotFoundError: No module named 'complex_networks_laboratories'`

- [ ] **Step 3: Rename package, update `pyproject.toml`, remove `scipy`**
  - Run `git mv src/web_edu_complex_network src/complex_networks_laboratories`
  - Remove `docs/superpowers/plans/2026-10-14-gold-layer-etl.md`
  - Update `pyproject.toml`:
    - `name = "complex-networks-laboratories"`
    - `description = "Complex network analysis laboratories (Sieci Złożone) - New Zealand scientific collaboration network"`
    - Remove `"scipy>=1.10.0"` from `dependencies`
    - `complex-networks = "complex_networks_laboratories.cli:app"` in `[project.scripts]`
    - `packages = ["src/complex_networks_laboratories"]`
    - `known-first-party = ["complex_networks_laboratories"]`
  - Run `uv sync` to regenerate `uv.lock`.

- [ ] **Step 4: Verify test passes and formatting is clean**
  Run: `uv run pytest tests/test_smoke.py && uv run ruff check . && uv run ruff format --check .`
  Expected: PASS

- [ ] **Step 5: Commit**
  ```bash
  git add -A src tests pyproject.toml uv.lock
  git commit -m "refactor: rename package to complex_networks_laboratories and remove scipy"
  ```

---

### Task 2: Data directory restructure & direct graph loader (`graph/loader.py`)

Eliminates the entire Medallion ETL pattern (Bronze/Silver/Gold) in favor of a clean, direct loader.

**Files:**
- Create: `data/new_zealand_collab/nodes.csv`, `data/new_zealand_collab/edges.csv`, `data/new_zealand_collab/gprops.csv` (moved from `data/temp_folder/network.csv`)
- Delete: `data/temp_folder/`, `data/bronze/`, `data/silver/`, `data/gold/`, `src/complex_networks_laboratories/etl/`, `tests/etl/`
- Modify: `src/complex_networks_laboratories/config.py`
- Create: `src/complex_networks_laboratories/graph/loader.py`
- Create: `tests/graph/test_loader.py`

**Interfaces:**
- `config.py`:
  - `DATA_DIR = PROJECT_ROOT / "data"`
  - `DATASET_DIR = DATA_DIR / "new_zealand_collab"`
  - `NODES_CSV_PATH = DATASET_DIR / "nodes.csv"`
  - `EDGES_CSV_PATH = DATASET_DIR / "edges.csv"`
  - `GPROPS_CSV_PATH = DATASET_DIR / "gprops.csv"`
- `graph/loader.py`:
  - `load_graph(nodes_path: Path = NODES_CSV_PATH, edges_path: Path = EDGES_CSV_PATH) -> nx.Graph`

- [ ] **Step 1: Write failing unit tests for graph loader** in `tests/graph/test_loader.py`:

```python
from pathlib import Path
import networkx as nx
import pytest
from complex_networks_laboratories.config import NODES_CSV_PATH, EDGES_CSV_PATH
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
```

- [ ] **Step 2: Run test to verify failure**
  Run: `uv run pytest tests/graph/test_loader.py`
  Expected: FAIL with `ModuleNotFoundError: No module named 'complex_networks_laboratories.graph.loader'`

- [ ] **Step 3: Move data files and implement `loader.py`**
  - Create `data/new_zealand_collab` and copy files from `data/temp_folder/network.csv/`:
    ```bash
    mkdir -p data/new_zealand_collab
    cp data/temp_folder/network.csv/nodes.csv data/new_zealand_collab/
    cp data/temp_folder/network.csv/edges.csv data/new_zealand_collab/
    cp data/temp_folder/network.csv/gprops.csv data/new_zealand_collab/
    rm -rf data/temp_folder data/bronze data/silver data/gold
    git rm -r --ignore-unmatch data/bronze data/silver data/gold
    ```
  - Update `src/complex_networks_laboratories/config.py` with simplified paths.
  - Delete `src/complex_networks_laboratories/etl/` and `tests/etl/`.
  - Implement `src/complex_networks_laboratories/graph/loader.py`:
    - Read `nodes.csv` skipping `# index` header, parsing `node_id = int(row[0])` and `name = row[1]`.
    - Read `edges.csv` skipping `# source` header, parsing `u = int(row[0])`, `v = int(row[1])`, `weight = int(row[3])`.
    - Return `G`.

- [ ] **Step 4: Run tests and verify passing**
  Run: `uv run pytest && uv run ruff check . && uv run ruff format --check .`
  Expected: PASS with 100% test success.

- [ ] **Step 5: Commit**
  ```bash
  git add -A data src tests
  git commit -m "feat(graph): implement direct graph loader from new_zealand_collab CSVs and remove ETL layer"
  ```

---

### Task 3: Interactive CLI (`info`), complete Markdown documentation update & project cleanup

**Files:**
- Modify: `src/complex_networks_laboratories/cli.py`
- Modify: `tests/test_smoke.py`
- Rewrite: `README.md`
- Rewrite: `docs/dataset_description.md`
- Update: `ADR_DATASET_MIGRATION.md`
- Delete: `docs/superpowers/plans/2026-10-14-gold-layer-etl.md` (untracked, obsolete)
- Mark superseded: `docs/superpowers/plans/2026-10-14-silver-layer-etl.md`

**Interfaces:**
- CLI commands:
  - `complex-networks version`
  - `complex-networks info` (loads graph via `load_graph()` and prints key graph metrics: nodes, edges, density, connected components, top hub institutions)

- [ ] **Step 1: Write CLI info test** in `tests/test_smoke.py`:

```python
def test_cli_info_command() -> None:
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "New Zealand Scientific Collaboration Network" in result.stdout
    assert "Nodes: 1,511" in result.stdout
    assert "Edges: 4,273" in result.stdout
```

- [ ] **Step 2: Run test to verify failure**
  Run: `uv run pytest tests/test_smoke.py::test_cli_info_command`
  Expected: FAIL

- [ ] **Step 3: Implement clean CLI in `cli.py`**
  - In `cli.py`, remove all ETL subcommands.
  - Implement `info` command to call `load_graph()` and display:
    - Dataset name & origin
    - Nodes count (1,511), Edges count (4,273), Graph density
    - Number of connected components (24, largest component: 1,463 nodes)
    - Top 3 institutions by degree (e.g. University of Auckland: degree 551)

- [ ] **Step 4: Update all project Markdown documentation (`.md` files)**
  1. **`README.md`**:
     - Project title: `complex-networks-laboratories` (Complex Networks / *Sieci Złożone*, Semester 5).
     - Dataset description: New Zealand Scientific Collaboration Network (`new_zealand_collab`).
     - Layout tree: show `data/new_zealand_collab/` and `src/complex_networks_laboratories/` (without `etl/`).
     - Usage guide: `uv sync`, `uv run complex-networks info`, `uv run complex-networks version`, running tests with `pytest` and `tox`.
  2. **`docs/dataset_description.md`**:
     - Complete formal description required for *Zadanie 1* evaluation:
       - **Source & Citation:** Aref et al. (ACSW '18), DOI `10.1145/3167918.3167920`, Figshare DOI `10.6084/m9.figshare.5705167`.
       - **Vertices ($|V|=1,511$):** Research institutions in New Zealand (universities, Crown Research Institutes, hospitals, industrial labs).
       - **Edges ($|E|=4,273$):** Co-authorship relationships with joint publication count (weights 1..1039).
       - **Physical / System Phenomenon:** National scientific knowledge production and research collaboration topology.
       - **Max Flow Interpretation:** Capacity of collaborative knowledge transfer and research capacity between institutions.
       - **Constraint verification table:** $|V| \in [1000, 5000]$, $|E| \in [3000, 30000]$ (both satisfied).
       - **Topology summary:** 24 connected components (giant component of 1,463 nodes), 932 odd-degree vertices (non-Eulerian).
  3. **`ADR_DATASET_MIGRATION.md`**:
     - Add status amendment note: Record that the initial ETL-based migration was streamlined to direct CSV ingestion via `graph/loader.py`, as native weights and labels rendered synthetic Medallion processing redundant.
  4. **Superpowers plans cleanup**:
     - Delete untracked `docs/superpowers/plans/2026-10-14-gold-layer-etl.md`.
     - Add deprecation notice header to `docs/superpowers/plans/2026-10-14-silver-layer-etl.md` indicating it was superseded by the direct loader architecture.

- [ ] **Step 5: Run all checks, tests, and tox**
  Run: `uv run pytest && uv run ruff check . && uv run ruff format --check . && uv run tox`
  Expected: ALL PASS.

- [ ] **Step 6: Verify no stale references remain**
  Run: `grep -rni "web_edu\|web-edu\|3031\|6474\|scipy" src tests README.md docs/`
  Expected: No matches (except historical mentions in ADR / archive plan).

- [ ] **Step 7: Commit**
  ```bash
  git add README.md docs ADR_DATASET_MIGRATION.md src/complex_networks_laboratories/cli.py tests/test_smoke.py
  git commit -m "docs: document new_zealand_collab dataset and provide CLI info command"
  ```
