# Architecture Decision Record (ADR) & Conversation Scope

**Doc ID:** ADR-0001  
**Status:** ACCEPTED  
**Date:** 2026-10-14  
**Project:** Complex Networks Lab (*Sieci Złożone*, Semestr 5)  
**Target Repository:** `/Users/piotrhirkyj/Documents/Obsidian/Studia/Semestr 5/Sieci złożone/Laboratoria/Labki`  
**Audience:** Autonomous AI coding agents, pair programmers, course evaluators  

---

## 1. Executive Summary

This document specifies the background, analysis, and execution plan for migrating the project's primary complex network dataset from `web-edu` to **`new_zealand_collab`**.

The migration:
1. **Eliminates synthetic hacks:** Replaces artificially generated edge weights and dummy node names (`page_X`) with real-world bibliometric collaboration counts and actual institution names.
2. **Simplifies the codebase:** Removes ~50+ lines of synthetic weight generation, complex CLI flags, and the `scipy.io.mmread` MatrixMarket parsing dependency in favor of clean CSV tabular processing.
3. **Optimizes semester-long computing:** At $|V|=1,511$ and $|E|=4,273$ (average degree $\approx 2.83$), algorithms like Edmonds-Karp ($O(V \cdot E^2)$) and Betweenness Centrality ($O(V \cdot E)$) execute in milliseconds without combinatorial explosion.

> [!NOTE]
> **Architecture Amendment (2026-10-14):**  
> Following architectural review and validation against `data/temp_folder`, the initial Medallion ETL pipeline (`bronze` -> `silver` -> `gold`, `etl/silver.py`, CLI `etl` commands) was completely eliminated in favor of **direct ingestion** via `complex_networks_laboratories.graph.loader:load_graph()`. Because `new_zealand_collab` natively provides clean institution names and Scopus co-authorship weights, intermediate disk copies were redundant. The graph loads directly into NetworkX in ~15 ms.

---

## 2. Course & Assignment Context (Zadanie 1)

* **Course:** *Sieci Złożone* (Complex Networks), Semester 5.
* **Scope of Selection:** A single dataset chosen in *Zadanie 1* is used continuously throughout the **entire semester**.
* **Hard Constraints:**
  * Number of vertices: $|V| \in [\sim 1000, 5000]$
  * Number of edges: $|E| \in [\sim 3000, 30000]$
* **Deliverables for Zadanie 1:**
  1. Formal description of:
     * What vertices represent.
     * What edges represent.
     * What system or physical phenomenon the network represents.
  2. Ingestion pipeline into modular Python code.
  3. Interactive/CLI algorithms:
     * **Shortest path** between two user-selected nodes (Dijkstra / BFS).
     * **Eulerian check & path finding** (checking if Eulerian or semi-Eulerian, finding the Eulerian trail/cycle via Hierholzer's algorithm on the graph or an induced subgraph).
     * **Maximum flow** between two user-selected nodes (Edmonds-Karp / Dinic).

---

## 3. Dataset Evaluation & Historical Evolution

During the design phase, multiple candidates across public repositories ([NetworkRepository](https://networkrepository.com), [KONECT](http://konect.cc), [Netzschleuder](https://networks.skewed.de), [SNAP](https://snap.stanford.edu), [ICON](https://icon.colorado.edu)) were analyzed:

| Dataset | Source | $|V|$ | $|E|$ | Weights | Labels | Decision & Rationale |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **`soc-wiki-Vote`** | NetworkRepository | 889 | 2,914 | No | No | **REJECTED**: Both $|V| < 1000$ and $|E| < 3000$; risk of rejection by strict grading criteria. |
| **`wiki-Vote`** | Stanford SNAP | 7,115 | 103,689 | No | No | **REJECTED**: Too large ($|V| > 5000, |E| > 30000$). |
| **`web-edu`** | NetworkRepository | 3,031 | 6,474 | No | No | **INITIAL / DEPRECATED**: Perfectly fit dimensions, but unweighted and unlabelled. Required synthetic weights (`--weight-mode random/constant`) and dummy node names, undermining physical interpretation of Max Flow. |
| **`web-spam`** | NetworkRepository | 4,767 | 37,375 | No | No | **REJECTED**: $|E| > 30000$ (by ~25%). High average degree ($\approx 15.7$) causes high runtime on later backtracking/centrality labs. |
| **`opsahl-usairport`** | KONECT | 1,574 | 28,236 | Yes | Yes (IATA) | **STRONG CANDIDATE**: Excellent, but higher edge density ($28k$). |
| **`new_zealand_collab`** | Netzschleuder / ICON | **1,511** | **4,273** | **Yes** | **Yes** | **SELECTED (WINNER)**: Ideal dimensions, real institutional names, real positive co-authorship counts, low density, lightweight. |

---

## 4. Target Dataset Specification: `new_zealand_collab`

* **Title:** New Zealand Scientific Collaborations (2010–2015)
* **Permanent URL:** `https://networks.skewed.de/net/new_zealand_collab`
* **Raw Download:** `https://networks.skewed.de/net/new_zealand_collab/files/new_zealand_collab.csv.zip`
* **Academic Citation:** S. Aref, D. Friggens, and S. Hendy, *"Analysing scientific collaborations of New Zealand institutions using Scopus bibliometric data."* Proc. Australasian Comp. Sci. Week Multiconf. (ACSW ’18), Article 49, 1–10 (2018).
* **Graph Type:** Undirected, weighted, labeled network.
* **Semantics for Lab Evaluation:**
  * **System:** Inter-institutional scientific collaboration and knowledge co-production network in New Zealand.
  * **Vertices (1,511):** Academic institutions, universities (e.g. University of Auckland, Otago), Crown Research Institutes, hospitals, and industrial research labs.
  * **Edges (4,273):** Joint scientific co-authorship between researchers affiliated with pairs of institutions.
  * **Edge Weight:** Integer count of joint publications indexed in Scopus (2010–2015).
  * **Max Flow Interpretation:** Capacity of scientific collaboration / research knowledge transfer between institutions.

---

## 5. Refactoring Blueprint for the Next Agent

The next agent should execute the following changes in the repository:

### 5.1. Data Ingestion (`data/bronze/`)
1. Download `new_zealand_collab.csv.zip`.
2. Extract into `data/bronze/`:
   * `data/bronze/nodes.csv` (contains `# index, _graphml_vertex_id, _pos`)
   * `data/bronze/edges.csv` (contains `# source, target, _graphml_edge_id, weight`)
   * `data/bronze/gprops.csv` (metadata)
3. Remove old `web-edu.mtx`, `readme.txt`, `readme.html`.

### 5.2. Path Configuration (`src/web_edu_complex_network/config.py`)
1. Replace `RAW_MTX_PATH` with:
   * `RAW_BRONZE_NODES_PATH = DATA_BRONZE_DIR / "nodes.csv"`
   * `RAW_BRONZE_EDGES_PATH = DATA_BRONZE_DIR / "edges.csv"`
2. Keep silver and gold directory constants.
3. Rename package/references if desired or maintain modular naming.

### 5.3. ETL Simplification (`src/web_edu_complex_network/etl/silver.py`)
1. **REMOVE:** `generate_edge_weights(...)` function and its tests completely.
2. **REMOVE:** `scipy.io` / `mmread` imports.
3. **REFACTOR:** `build_silver_tables(...)` to read the raw CSVs:
   * Node mapping:
     * `node_id`: integer index from raw `nodes.csv`.
     * `name`: string from raw `_graphml_vertex_id` (real institution name).
     * `degree`: degree calculated in NetworkX or from edges table.
     * `is_even_degree`: `(degree % 2 == 0)`.
   * Edge mapping:
     * `source`: integer.
     * `target`: integer.
     * `weight`: float/int from raw `weight` column (Scopus publication count).
     * `capacity`: float equal to `weight` (natural flow capacity).
4. Persist to standard Silver tables: `data/silver/nodes.csv` and `data/silver/edges.csv`.

### 5.4. CLI Cleanup (`src/web_edu_complex_network/cli.py`)
1. Strip `--weight-mode`, `--seed`, `--min-weight`, `--max-weight` options from the `etl silver` command.
2. The command simply runs: `uv run <cli> etl silver`.

### 5.5. Test Suite (`tests/etl/test_etl_silver.py`)
1. Remove tests for synthetic weight modes (`test_generate_edge_weights_*`).
2. Update shape asserts:
   * `len(nodes) == 1511`
   * `len(edges) == 4273`
3. Assert that node names match real institutions (e.g. non-empty string, not `page_X`).
4. Assert edge weights are positive numbers matching source data.

### 5.6. Documentation (`docs/dataset_description.md` & `README.md`)
1. Replace the academic web hyperlink description with the Scopus New Zealand collaboration description.
2. Update node/edge counts ($1,511$ / $4,273$).

---

## 6. Downstream Architecture for Algorithms (Upcoming Steps)

Once the Silver layer ETL is updated, subsequent development proceeds to:
1. **`src/.../graph/model.py`:** Load Silver `nodes.csv` and `edges.csv` into a typed `networkx.Graph` with attributes `weight`, `capacity`, and node `name`.
2. **`src/.../algorithms/shortest_path.py`:** Weighted Dijkstra vs unweighted BFS with pretty-printed institution paths.
3. **`src/.../algorithms/eulerian.py`:** Check Eulerian / semi-Eulerian status; extract connected component/subgraph if needed; run Hierholzer's algorithm.
4. **`src/.../algorithms/max_flow.py`:** Edmonds-Karp algorithm using the Scopus publication capacity attribute.
