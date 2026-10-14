# Dataset Description: `web-edu`

## 1. Overview and Source
* **Dataset Name:** `web-edu`
* **Category:** Web Graphs / Sparse Hyperlink Networks
* **Source Repository:** [Network Data Repository](http://networkrepository.com)
* **Citation:**
  > Ryan A. Rossi and Nesreen K. Ahmed, *"The Network Data Repository with Interactive Graph Analytics and Visualization"*, AAAI, 2015.

```bibtex
@inproceedings{nr,
    title={The Network Data Repository with Interactive Graph Analytics and Visualization},
    author={Ryan A. Rossi and Nesreen K. Ahmed},
    booktitle={AAAI},
    url={http://networkrepository.com},
    year={2015}
}
```

---

## 2. Quantitative Characteristics & Constraints Verification
The laboratory assignment sets strict criteria for the dataset size:
* **Target Vertices:** ~1,000 – 5,000
* **Target Edges:** ~3,000 – 30,000

| Metric | Required Range | `web-edu` Dataset | Status |
| :--- | :--- | :--- | :--- |
| **Number of Vertices ($|V|$)** | $1\,000 \le |V| \le 5\,000$ | **3,031** | **Satisfied** |
| **Number of Edges ($|E|$)** | $3\,000 \le |E| \le 30\,000$ | **6,474** | **Satisfied** |
| **Average Degree** | N/A | $\approx 4.27$ | Sparse network |
| **Graph Type** | N/A | Symmetric / Undirected | Sparse Coordinate Matrix (`.mtx`) |

---

## 3. Domain Interpretation & Phenomenon

### What do the vertices (nodes) represent?
Each vertex in the graph represents an individual **web page or document** hosted within educational and academic domains (such as `.edu` institutional websites).

### What do the edges represent?
Each edge represents a **hyperlink (URL anchor)** connecting two web pages, establishing an informational bridge between academic content.

### What real-world system or phenomenon is modeled?
The graph models the **navigational and topological architecture of academic cyberspace**:
1. **Information Retrieval & Web Surfing:** Models how human users and web crawlers traverse institutional websites via click streams.
2. **Authority and PageRank:** Reflects authority distribution across departmental domains, where central hubs connect numerous specialized pages.
3. **Clustering & Communities:** Captures departmental affinities, institutional collaborations, and resource linking within academia.
4. **Resilience & Bottlenecks:** Demonstrates how critical bridge pages facilitate flow across otherwise isolated sub-communities, relevant to maximum flow and connectivity analyses.
