# Silver Layer ETL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a robust, reproducible ETL transformation pipeline from raw MatrixMarket (`data/bronze/web-edu.mtx`) into relational Silver tables (`data/silver/nodes.csv` and `data/silver/edges.csv`) with validated node/edge attributes.

**Architecture:** A dedicated ETL module (`web_edu_complex_network.etl.silver`) that parses the raw MatrixMarket coordinate format, computes node-level topological metrics (`degree`, `is_even_degree`, `name`), configures edge weights (`constant` or seeded `random`) along with unit flow `capacity`, and serializes the result into standardized CSV files. The pipeline is exposed via a Typer CLI subcommand `web-edu etl silver`.

**Tech Stack:** Python 3.13, NetworkX, SciPy, Typer, Pytest, Ruff.

**Spec:** Requirements defined in laboratory Task 1 and user specification:
* Nodes: `node_id` (1-indexed 1..3031), `name` (`page_<id>`), `degree` (int), `is_even_degree` (bool).
* Edges: `source` (int), `target` (int), `weight` (float, constant or seeded random), `capacity` (float, required for max flow).

## Global Constraints

* Language for code, docstrings, CLI help, and documentation: English.
* Strict dependency on project layout (`src/web_edu_complex_network/`).
* Type annotations on all public functions; strictly pass `ruff check` and `ruff format`.
* Deterministic behavior: when `--weight-mode random` is selected, `--seed` MUST yield identical weights across runs.
* Edge weights MUST be strictly positive ($w > 0$) to support shortest-path algorithms.

## Review Focus

* **Duplicate edge deduplication:** MatrixMarket symmetric format may define undirected edges or lower-triangular coordinates; verify no duplicate undirected pairs `(u, v)` and `(v, u)` exist in `edges.csv`.
* **Degree calculation fidelity:** Ensure `degree` in `nodes.csv` exactly matches the degree computed from the deduplicated edge list.
* **Positive weights invariant:** Ensure `random` weight generation never generates non-positive numbers ($w \le 0$).
* **File non-corruption on failure:** If an ETL error occurs during processing, ensure partial files are not left in an inconsistent state (write to temp/clean atomic write).
* **CLI exit codes:** Proper error exit code (non-zero) when invalid parameters or modes are passed to the CLI.

---

### Task 1: Core Silver Data Models and Weight Generation Logic

**Files:**
* Create: `src/web_edu_complex_network/etl/silver.py`
* Modify: `src/web_edu_complex_network/config.py`
* Test: `tests/etl/test_etl_silver.py`

**Interfaces:**
* Consumes: `RAW_MTX_PATH`, `DATA_SILVER_DIR` from `config.py`
* Produces:
  * `generate_edge_weights(edge_count: int, mode: str, seed: int | None, min_val: float, max_val: float) -> list[float]`
  * `build_silver_tables(mtx_path: Path, weight_mode: str, seed: int | None) -> tuple[list[dict], list[dict]]`

- [ ] **Step 1: Write the failing unit tests for weight generator and model builders**

```python
from pathlib import Path
import pytest
from web_edu_complex_network.etl.silver import generate_edge_weights, build_silver_tables
from web_edu_complex_network.config import RAW_MTX_PATH


def test_generate_edge_weights_constant():
    weights = generate_edge_weights(
        edge_count=10, mode="constant", seed=None, min_val=1.0, max_val=1.0
    )
    assert len(weights) == 10
    assert all(w == 1.0 for w in weights)


def test_generate_edge_weights_random_seeded():
    w1 = generate_edge_weights(edge_count=100, mode="random", seed=42, min_val=1.0, max_val=5.0)
    w2 = generate_edge_weights(edge_count=100, mode="random", seed=42, min_val=1.0, max_val=5.0)
    assert len(w1) == 100
    assert w1 == w2
    assert all(1.0 <= w <= 5.0 for w in w1)


def test_build_silver_tables_shapes():
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/etl/test_etl_silver.py -v`
Expected: FAIL with `ModuleNotFoundError` or `ImportError`.

- [ ] **Step 3: Implement data models, weight generator, and table builder in `src/web_edu_complex_network/etl/silver.py`**

Add config constants in `src/web_edu_complex_network/config.py`:
* `SILVER_NODES_CSV_PATH = DATA_SILVER_DIR / "nodes.csv"`
* `SILVER_EDGES_CSV_PATH = DATA_SILVER_DIR / "edges.csv"`

Implement in `src/web_edu_complex_network/etl/silver.py`:
* `generate_edge_weights(...)` using Python `random.Random(seed)`.
* `build_silver_tables(mtx_path, weight_mode, seed)` reading coordinates with `scipy.io.mmread`, constructing the graph, extracting nodes `1..3031`, degrees, and formatting attributes.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/etl/test_etl_silver.py -v`
Expected: PASS.

- [ ] **Step 5: Run linter and formatter**

Run: `uv run ruff check . && uv run ruff format --check .`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/web_edu_complex_network/config.py src/web_edu_complex_network/etl/silver.py tests/etl/test_etl_silver.py
git commit -m "feat(etl): implement core silver transformation logic and weight generator"
```

---

### Task 2: CSV Persistence and Atomic File Writing

**Files:**
* Modify: `src/web_edu_complex_network/etl/silver.py`
* Modify: `tests/etl/test_etl_silver.py`

**Interfaces:**
* Consumes: `build_silver_tables`
* Produces:
  * `save_silver_tables(nodes: list[dict], edges: list[dict], nodes_path: Path, edges_path: Path) -> tuple[Path, Path]`
  * `run_silver_pipeline(weight_mode: str, seed: int | None, min_weight: float, max_weight: float) -> tuple[Path, Path]`

- [ ] **Step 1: Write the failing unit tests for CSV persistence and pipeline execution**

```python
import csv


def test_run_silver_pipeline_creates_files(tmp_path):
    nodes_csv = tmp_path / "nodes.csv"
    edges_csv = tmp_path / "edges.csv"
    from web_edu_complex_network.etl.silver import build_silver_tables, save_silver_tables

    nodes, edges = build_silver_tables(RAW_MTX_PATH, weight_mode="constant", seed=None)
    save_silver_tables(nodes, edges, nodes_csv, edges_csv)

    assert nodes_csv.exists()
    assert edges_csv.exists()

    with open(nodes_csv, mode="r", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 3031
        assert rows[0]["name"] == "page_1"
        assert rows[0]["is_even_degree"] in ["True", "False"]

    with open(edges_csv, mode="r", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 6474
        assert float(rows[0]["weight"]) == 1.0
        assert float(rows[0]["capacity"]) == 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/etl/test_etl_silver.py -k test_run_silver_pipeline_creates_files -v`
Expected: FAIL with `ImportError: cannot import name 'save_silver_tables'`.

- [ ] **Step 3: Implement `save_silver_tables` and `run_silver_pipeline` in `src/web_edu_complex_network/etl/silver.py`**

Use Python standard library `csv.DictWriter` to write `nodes.csv` and `edges.csv` atomically with clean UTF-8 headers.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/etl/test_etl_silver.py -v`
Expected: PASS.

- [ ] **Step 5: Run linter and formatter**

Run: `uv run ruff check . && uv run ruff format --check .`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/web_edu_complex_network/etl/silver.py tests/etl/test_etl_silver.py
git commit -m "feat(etl): add csv serialization and full silver pipeline runner"
```

---

### Task 3: CLI Subcommand Integration for Silver ETL

**Files:**
* Modify: `src/web_edu_complex_network/cli.py`
* Modify: `src/web_edu_complex_network/etl/__init__.py`
* Modify: `tests/etl/test_etl_silver.py`

**Interfaces:**
* Consumes: `run_silver_pipeline` from `etl.silver`
* Produces:
  * CLI command: `web-edu etl silver [--weight-mode constant|random] [--seed 42] [--min-weight 1.0] [--max-weight 5.0]`

- [ ] **Step 1: Write failing CLI integration test**

```python
from typer.testing import CliRunner
from web_edu_complex_network.cli import app

runner = CliRunner()


def test_cli_etl_silver_constant():
    result = runner.invoke(app, ["etl", "silver", "--weight-mode", "constant"])
    assert result.exit_code == 0
    assert "Silver tables successfully created" in result.stdout


def test_cli_etl_silver_invalid_mode():
    result = runner.invoke(app, ["etl", "silver", "--weight-mode", "invalid_mode"])
    assert result.exit_code != 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/etl/test_etl_silver.py -k test_cli_etl_silver -v`
Expected: FAIL with `No such command 'etl'`.

- [ ] **Step 3: Implement `etl` sub-typer and `silver` command in `src/web_edu_complex_network/cli.py`**

* Create `etl_app = typer.Typer(help="ETL pipeline commands for data layers.")`
* Add command `silver(...)` taking options `--weight-mode`, `--seed`, `--min-weight`, `--max-weight`.
* Export `run_silver_pipeline` in `src/web_edu_complex_network/etl/__init__.py`.
* Register `app.add_typer(etl_app, name="etl")`.

- [ ] **Step 4: Run tests to verify all pass**

Run: `uv run pytest tests/etl/test_etl_silver.py -v`
Expected: PASS.

- [ ] **Step 5: Run full test suite and linters**

Run: `uv run ruff check . && uv run ruff format --check . && uv run pytest`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/web_edu_complex_network/cli.py src/web_edu_complex_network/etl/__init__.py tests/etl/test_etl_silver.py
git commit -m "feat(cli): add etl silver command with configurable weight modes"
```

---

### Task 4: End-to-End Execution and Tox Verification

**Files:**
* Modify: `README.md`
* Output files generated: `data/silver/nodes.csv`, `data/silver/edges.csv`

- [ ] **Step 1: Execute the pipeline via CLI to generate default Silver data**

Run: `uv run web-edu etl silver --weight-mode constant`
Expected output: Success message confirming creation of `nodes.csv` (3031 rows) and `edges.csv` (6474 rows).

- [ ] **Step 2: Verify generated CSV contents and integrity**

Run:
```bash
uv run python -c "
import csv
with open('data/silver/nodes.csv') as f:
    assert len(list(csv.DictReader(f))) == 3031
with open('data/silver/edges.csv') as f:
    assert len(list(csv.DictReader(f))) == 6474
print('Silver tables verified successfully!')
"
```
Expected: `Silver tables verified successfully!`

- [ ] **Step 3: Update README.md with Silver ETL documentation**

Add documentation under `## CLI Usage` demonstrating `uv run web-edu etl silver`.

- [ ] **Step 4: Run full tox validation**

Run: `uv run tox`
Expected: All environments (`lint`, `py313`) pass.

- [ ] **Step 5: Commit**

```bash
git add README.md data/silver/
git commit -m "docs: document silver etl pipeline and add verified silver artifacts"
```
