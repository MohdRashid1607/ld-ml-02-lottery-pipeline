# Product Benchmark & Architectural Comparison — LD-ML-02

## 1. Comparable Lottery-Data Products Benchmark

| Product | Strengths / Features | Weaknesses / Gaps | Project Decision (Adopt / Adapt / Reject) |
| :--- | :--- | :--- | :--- |
| **The National Lottery Draw History** (Official) | Official source authority, recent draw archive, official draw numbers. | Limited ~180 day rolling window; no weather enrichment; Next.js frontend scraper resistance. | **Adopt as primary extraction source**; adapt by building local persistent relational SQLite storage. |
| **Beat Lottery** (`beatlottery.co.uk`) | Full multi-year archive, CSV export, descriptive statistics. | Mixes descriptive data with predictive/gambling claims; hides scraping methodology. | **Adopt clean CSV export concepts**; **Reject** all prediction tools in favor of strict randomness ethics. |
| **Results.co.uk** | Clean table displays, year navigation. | No machine-readable API, lacks provenance metadata. | **Adapt table layout ideas** for our Streamlit UI; add quality provenance badges. |
| **LotteryData.io / API-Verve** | Versioned REST endpoints, structured JSON responses. | Commercial API with high paywalls and restrictive request limits. | **Adapt schema design** (ISO 8601 timestamps, structured JSON/CSV export) without external subscription dependencies. |
| **Community EuroMillions API** | Historical results via GitHub community. | Unverified provenance, prone to downtime and lack of schema maintenance. | **Reject** as data source; only use verified official website extraction. |
| **Kaggle Lottery Datasets** | Downloadable CSV/SQLite files, good for data science. | Static snapshots; lacks automated incremental updates and real-time enrichment. | **Adopt Kaggle-style data dictionary & clean normalization**; implement live incremental updates. |

---

## 2. Key Architectural Decisions

1. **Separation of Concerns**: Extracted fetching, parsing, validation, persistence, and presentation into dedicated Python packages (`src/collectors`, `src/database`, `src/validation`, `src/weather`, `app/`).
2. **Defensive Validation**: Strict rules in `config/game_rules.yaml` prevent corrupt or out-of-range records from entering the database.
3. **Meteorological Enrichment**: Enriched draw events with Paris and London historical temperatures using Open-Meteo archive API.
4. **Lightweight Interactive Explorer**: Created Streamlit multi-tab and single-page data exploration application with live filtering, analytics, and schema-compliant exports.
