# Dataset Description: `new_zealand_collab`

## 1. Overview and Source
* **Dataset Name:** `new_zealand_collab` (New Zealand Scientific Collaborations, 2010–2015)
* **Category:** Bibliometric Collaboration Networks / Institutional Graphs
* **Source Repository:** [Netzschleuder](https://networks.skewed.de/net/new_zealand_collab) & [ICON](https://icon.colorado.edu)
* **Permanent URL:** `https://networks.skewed.de/net/new_zealand_collab`
* **Data Figshare DOI:** [10.6084/m9.figshare.5705167](https://doi.org/10.6084/m9.figshare.5705167)
* **Academic Citation:**
  > S. Aref, D. Friggens, and S. Hendy, *"Analysing scientific collaborations of New Zealand institutions using Scopus bibliometric data."* Proceedings of the Australasian Computer Science Week Multiconference (ACSW ’18), Article 49, 1–10 (2018). https://doi.org/10.1145/3167918.3167920

```bibtex
@inproceedings{aref2018analysing,
    title={Analysing scientific collaborations of New Zealand institutions using Scopus bibliometric data},
    author={Aref, Samin and Friggens, David and Hendy, Shaun},
    booktitle={Proceedings of the Australasian Computer Science Week Multiconference},
    pages={1--10},
    year={2018},
    doi={10.1145/3167918.3167920}
}
```

---

## 2. Quantitative Characteristics & Constraints Verification

The *Complex Networks* (*Sieci Złożone*) course specification defines strict sizing constraints for the semester dataset:
* **Target Vertices:** $1\,000 \le |V| \le 5\,000$
* **Target Edges:** $3\,000 \le |E| \le 30\,000$

| Metric | Course Requirement | `new_zealand_collab` | Status / Note |
| :--- | :--- | :--- | :--- |
| **Number of Vertices ($|V|$)** | $1\,000 \le |V| \le 5\,000$ | **1,511** | **Satisfied** |
| **Number of Edges ($|E|$)** | $3\,000 \le |E| \le 30\,000$ | **4,273** | **Satisfied** |
| **Average Degree ($\langle k \rangle$)** | N/A | $\approx 5.66$ | Sparse, tractable computation |
| **Graph Type** | N/A | Undirected, weighted | Real Scopus publication counts |
| **Edge Weight Range** | Strictly positive | $[1, 1\,039]$ | Median: 1, Max: 1,039 |
| **Connected Components** | N/A | **24** | Giant component has 1,463 nodes (96.8%) |
| **Eulerian Status** | Analyzed in Lab 1 | **Non-Eulerian** | 932 odd-degree vertices |

---

## 3. Domain Interpretation & Phenomenon

### What do the vertices (nodes) represent?
Each vertex represents an individual **research institution or organization** in New Zealand that produced academic output indexed in Elsevier's Scopus database between 2010 and 2015. These include:
- Major universities (e.g., University of Auckland, University of Otago, Massey University, Victoria University of Wellington).
- Crown Research Institutes (CRIs) (e.g., AgResearch, NIWA, GNS Science, Scion).
- District Health Boards (DHBs) and teaching hospitals.
- Private R&D firms and industrial research laboratories.

### What do the edges represent?
Each edge represents an undirected **scientific co-authorship relationship** between two institutions. An edge exists between institution $i$ and institution $j$ if at least one peer-reviewed publication co-authored by researchers affiliated with both institutions was published during the 2010–2015 period.

### What do the edge weights represent?
The edge weight is an **integer count** of joint scientific publications between the two institutions. 
* A weight of $1$ indicates an occasional cross-institutional co-authorship.
* High weights (e.g., between major universities such as Auckland and Otago) reflect strong institutional alliances, joint research grants, and high-volume knowledge co-production.
* In the context of the **Maximum Flow** problem (Zadanie 1), the edge weight represents the **collaborative throughput / knowledge transfer capacity** between institutions.

### What real-world system or phenomenon is modeled?
The graph models the **national scientific knowledge production system and research collaboration topology**:
1. **Core-Periphery Structure:** Research is heavily centralized around major university hubs (University of Auckland with degree 551, University of Otago with degree 406), which act as knowledge brokers for smaller institutions.
2. **Community Clustering:** Distinct sub-communities emerge corresponding to specialized research domains (e.g., agricultural research around AgResearch, marine sciences around NIWA).
3. **Resilience & Bottlenecks:** Evaluating bridges and maximum flow reveals structural dependencies—how regional hospitals and industrial labs rely on gateway universities to connect with the broader scientific ecosystem.
