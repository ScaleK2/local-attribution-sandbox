# Local Attribution Modelling Sandbox

A local-first attribution modelling sandbox built using Python, DuckDB, and stitched multi-touch marketing journeys.

This project simulates deterministic attribution models using stitched frontend and backend datasets to better understand:

- identity stitching,
- conversion journey reconstruction,
- attribution philosophy,
- channel roles,
- revenue reconciliation,
- and behavioural interpretation.

The purpose of this project is educational and experimental.

It is designed to help marketers, analysts, and engineers understand how attribution systems actually work beneath platform reporting interfaces.

---

# Who This Sandbox Is For

This project is designed for:

- marketers who feel platform reporting tells incomplete stories,
- analysts trying to better understand attribution logic,
- performance teams moving beyond spreadsheet workflows,
- and anyone curious about how customer journey measurement works underneath reporting interfaces.

No advanced data engineering background is required.

The sandbox is intentionally designed as a guided learning environment rather than a production attribution system.

---

# Why This Project Exists

Most marketers:
- trust platform attribution blindly,
- never inspect data quality,
- never validate joins,
- and rarely understand how attribution assumptions influence channel valuation.

This project intentionally rebuilds attribution modelling from scratch.

The goal is not:
> "find the perfect attribution model"

The goal is:
> understand how attribution frameworks shape interpretation.

---

# Why This Matters For Modern Marketers

Many marketers are still trapped in:
- Excel spreadsheets,
- disconnected platform exports,
- static dashboards,
- and fragmented reporting systems.

As datasets grow across:
- Google Ads,
- Meta,
- GA4,
- CRMs,
- backend systems,
- call centres,
- and offline conversions,

traditional spreadsheet workflows begin to break down.

This project demonstrates a lightweight local analytics workflow that allows marketers to:

- stitch identities across systems,
- reconcile frontend and backend datasets,
- analyse larger event-level datasets,
- reconstruct customer journeys,
- validate attribution assumptions,
- and generate strategic behavioural insights locally.

The goal is not to replace enterprise data infrastructure.

The goal is to help marketers:
- think more structurally,
- move beyond platform dashboards,
- and develop analytical systems thinking using accessible local tools.

This approach creates a bridge between:
- traditional marketing analysis,
- analytics engineering,
- and behavioural modelling.

---

# Key Concepts Covered

## Data Engineering
- Identity stitching
- Join logic
- Revenue validation
- Data reconciliation
- Deduplication

## Attribution Modelling
- First-touch attribution
- Last-touch attribution
- Linear attribution
- Position-based attribution
- Time-decay attribution

## Behavioural Interpretation
- Demand generation vs demand capture
- Funnel role analysis
- Assist behaviour
- Journey complexity
- Attribution bias

## Strategic Analytics
- Channel role interpretation
- Revenue inflation detection
- Tracking limitations
- Attribution ambiguity
- Deterministic model comparison

---

# Tech Stack

| Tool | Purpose |
|---|---|
| Python | Data processing |
| DuckDB | Local analytical database |
| Pandas | Data manipulation |
| CSV datasets | Simulated frontend/backend data |
| Ollama (optional) | Local LLM experimentation |

---

> # Recommended Starting Point

If you are new to attribution modelling:

1. Download the repository ZIP or clone the repo
2. Read docs/setup_guide.pdf
3. Open docs/attribution modelling walkthrough.pdf
4. Run each script sequentially inside scripts/core/

The project is designed as a guided walkthrough rather than a production attribution system.

---

# Quick Start

## 1. Clone the Repository

```bash
git clone https://github.com/ScaleK2/local-attribution-sandbox.git
cd local-attribution-sandbox
```

---

## 2. Create a Virtual Environment (Optional / Recommended)

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Run the Attribution Workflow

Run scripts sequentially:

```bash
python scripts/01_stitch_data.py
python scripts/02_validate_data.py
python scripts/03_check_backend_truth_vs_stitched.py
python scripts/04_backend_first_conversion_journeys.py
python scripts/05_build_touchpoint_attribution.py
python scripts/06_linear_attribution.py
python scripts/07_position_based_attribution.py
python scripts/08_time_decay_attribution.py
python scripts/09_compare_attribution_models.py
```

---

## 5. Follow Along With The Learning Guide

Open:

```text
docs/attribution modelling walkthrough.pdf
```

This contains:
- screenshots,
- commentary,
- model explanations,
- behavioural interpretation,
- and strategic insights.

---


# Project Architecture

```text
Raw datasets
    ↓
Identity stitching
    ↓
Validation layer
    ↓
Journey construction
    ↓
Attribution modelling
    ↓
Strategic interpretation
```

---

# Folder Structure

```text
local-attribution-sandbox/
│
├── data/
│   ├── ga4_events.csv
│   ├── google_ads_clicks.csv
│   ├── meta_ads_insights.csv
│   ├── backend_outcomes.csv
│   ├── data_dictionary.md
│   ├── simulation_summary.csv
│   ├── master_user_simulation.csv
│
├── scripts/
│   ├── 01_stitch_data.py
│   ├── 02_validate_data.py
│   ├── 03_check_backend_truth_vs_stitched.py
│   ├── 04_backend_first_conversion_journeys.py
│   ├── 05_build_touchpoint_attribution.py
│   ├── 06_linear_attribution.py
│   ├── 07_position_based_attribution.py
│   ├── 08_time_decay_attribution.py
│   ├── 09_compare_attribution_models.py
│
├── outputs/
│
├── docs/
│   ├── setup_guide.pdf
│   ├── attribution modelling walkthrough.pdf
│
├── requirements.txt
└── README.md
```

---

# Setup

## 1. Install Python

Download:
https://www.python.org/downloads/

Verify:

```bash
python --version
```

---

## 2. Install Dependencies

Inside the project folder:

```bash
pip install duckdb pandas
```

---

# Running the Project

Run scripts sequentially.

Example:

```bash
python scripts/01_stitch_data.py
```

Then continue through the pipeline.

---

# Example Learning Flow / What to expect

---

# Step 1 — Stitch Identity Data

## Script
```text
01_stitch_data.py
```

## Goal
Connect frontend marketing events with backend outcomes using shared identifiers.

## Key Insight
Identity quality determines attribution quality.

---

# Step 2 — Validate Data Structure

## Script
```text
02_validate_data.py
```

## Goal
Inspect schema, validate joins, and understand event quality.

## Key Insight
Bad joins create misleading attribution outputs.

---

# Step 3 — Validate Join Quality

## Scripts
```text
03_check_join_quality.py
03b_check_backend_truth_vs_stitched.py
```

## Goal
Detect:
- duplicate revenue,
- broken joins,
- inflated conversions,
- and mismatched identifiers.

## Key Insight
Revenue reconciliation is mandatory before attribution interpretation.

---

# Step 4 — Build Conversion Journeys

## Scripts
```text
04_build_conversion_journeys.py
04b_build_conversion_journeys_by_conversion_key.py
04c_backend_first_conversion_journeys.py
```

## Goal
Reconstruct chronological user journeys.

## Key Insight
Attribution is fundamentally journey analysis.

---

# Step 5 — First-Touch & Last-Touch Attribution

## Script
```text
05_build_touchpoint_attribution.py
```

## Goal
Compare:
- discovery channels,
- versus conversion capture channels.

## Key Insight
Different attribution philosophies create different strategic narratives.

---

# Step 6 — Linear Attribution

## Script
```text
06_linear_attribution.py
```

## Goal
Split revenue evenly across all touchpoints.

## Key Insight
Journeys are collaborative, not purely winner-take-all.

---

# Step 7 — Position-Based Attribution

## Script
```text
07_position_based_attribution.py
```

## Goal
Weight:
- first-touch heavily,
- last-touch heavily,
- middle touches lightly.

## Key Insight
Attribution models encode behavioural assumptions.

---

# Step 8 — Time-Decay Attribution

## Script
```text
08_time_decay_attribution.py
```

## Goal
Weight recent touchpoints more heavily.

## Key Insight
Recency influences attribution valuation significantly.

---

# Step 9 — Compare Attribution Models

## Script
```text
09_compare_attribution_models.py
```

## Goal
Compare all deterministic models side-by-side.

## Key Insight
The data did not change.
The assumptions changed.

---

# Major Findings From This Dataset

## Meta behaves primarily as a discovery channel
- Strong first-touch performance
- Weak last-touch performance
- High attribution sensitivity

Likely role:
- awareness,
- demand generation,
- early consideration.

---

## Google Ads behaves primarily as a conversion capture channel
- Strong last-touch performance
- Strong time-decay performance
- Stable across models

Likely role:
- intent capture,
- lower-funnel conversion,
- demand harvesting.

---

## Direct traffic remains ambiguous
Direct may represent:
- genuine brand recall,
- unattributed revisits,
- dark social,
- tracking leakage,
- or cross-device continuation.

Direct traffic should be interpreted cautiously.

---

# Critical Attribution Insight

The SAME conversions produced different strategic narratives depending on attribution philosophy.

This is the core lesson.

Attribution models are:
- heuristic frameworks,
- behavioural theories,
- operational lenses.

They are NOT objective truth.

---

# Limitations

This project intentionally simplifies reality.

Limitations include:
- deterministic logic,
- incomplete identity resolution,
- no impression/view-through attribution,
- no cross-device stitching,
- no incrementality testing,
- no probabilistic modelling,
- no MMM integration.

---

# Future Improvements

Potential next steps:

## Probabilistic Attribution
- Markov chains
- Removal effects
- Shapley values
- Transition modelling

## Infrastructure
- Sessionisation
- Event weighting
- Deduplication logic
- Channel grouping

## Visualisation
- Sankey diagrams
- Funnel flow maps
- Attribution comparison charts
- Path frequency analysis

## Machine Learning
- DDA simulation
- Conversion propensity scoring
- Journey clustering

---

# Important Strategic Insight

Attribution is not:
> finding truth.

Attribution is:
> distributing uncertainty according to behavioural assumptions.

That distinction changes how marketing should be interpreted.

---

# Recommended Reading / Concepts

- Multi-touch attribution
- Incrementality testing
- Marketing Mix Modelling (MMM)
- Markov attribution
- Shapley attribution
- Identity resolution
- Conversion lift studies
- Behavioural economics

---

# Final Note

This project intentionally prioritises:
- understanding,
- validation,
- behavioural reasoning,
- and systems thinking

over:
- platform black boxes,
- vanity dashboards,
- or surface-level ROAS reporting.

The objective is to think more deeply about:
- how marketing actually influences behaviour,
- and how measurement systems shape business decisions.