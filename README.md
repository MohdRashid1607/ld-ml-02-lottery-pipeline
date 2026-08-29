# 🎰 Lottery Data Acquisition & Draw-Weather Enrichment Pipeline (LD-ML-02)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linter-ruff-red.svg)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-pytest-orange.svg)](https://pytest.org/)

An enterprise-grade, reproducible Python pipeline that collects official historical lottery draw results (**EuroMillions**, **Thunderball**, **Set For Life**) and enriches every draw with its drawing venue city (**Paris** or **London**) and historical air temperature in **Degrees Celsius (°C)** from the Open-Meteo meteorological archive.

---

## 📌 Features & Architecture Overview

- **Modular Collector Framework**: Object-oriented architecture with `BaseCollector` handling HTTP sessions, bounded retries, and rate limiting; subclasses handle game-specific HTML scraping.
- **Defensive Data Validation**: Configuration-driven validation rules (`config/game_rules.yaml`) checking number counts, valid ball ranges, and duplicate prevention.
- **Relational SQLite Database**: Normalized schema with games, venues, draws, draw numbers, and weather readings.
- **Meteorological Enrichment**: Automated IANA timezone conversion (`Europe/Paris` and `Europe/London`) and historical temperature matching (Open-Meteo Archive API).
- **Interactive Data Explorer & Analytics**: Streamlit web interface with real-time filtering, detailed record provenance, statistical number frequency charts, and ISO 8601 / UTF-8 data export (CSV & JSON).
- **Automated Quality Assurance**: 100% passing `pytest` test suite with offline mocks, Black formatting, and Ruff linting.

---

## 📂 Repository Structure

```text
lottery-data-collector/
├── app/
│   └── main.py                     # Streamlit Interactive Data Explorer & Dashboard
├── config/
│   ├── game_rules.yaml             # Source URLs, ball rules, venues, and timezones
│   └── settings.py                 # Configuration loader module
├── data/
│   └── lottery.db                  # Normalized SQLite 3 Database
├── docs/
│   ├── day3_sql_examples.md        # Relational SQL query documentation
│   ├── day4_validation_report.md   # Defensive validation test outputs
│   ├── day5_full_dataset_run.md    # EuroMillions collection run logs
│   ├── day5_qa_sample.md           # 10-draw manual QA verification sheet
│   ├── day6_design_note.md         # Software engineering principles & refactoring note
│   ├── day7_thunderball_qa.md      # Thunderball manual QA verification sheet
│   ├── day8_set_for_life_qa.md     # Set For Life manual QA verification sheet
│   ├── day9_audit_report.md        # Data quality and completeness audit report
│   ├── location_weather_assessment.md # Official venues and weather methodology
│   ├── product_benchmark.md        # Industry product benchmark & comparison
│   └── prompt_log.md               # LLM interaction & prompt engineering log
├── logs/
│   └── activity.log                # Pipeline execution and runtime log
├── src/
│   ├── collectors/
│   │   ├── base.py                 # Abstract BaseCollector class (HTTP/retry logic)
│   │   ├── euromillions.py         # EuroMillions parser
│   │   ├── thunderball.py          # Thunderball parser
│   │   ├── set_for_life.py         # Set For Life parser
│   │   └── fetch_draw.py           # Legacy fetcher utility
│   ├── database/
│   │   ├── db.py                   # SQLite schema, connection, and parameterized inserts
│   │   ├── init_db.py              # Database initializer script
│   │   └── collect_history.py      # Historical batch runner
│   ├── validation/
│   │   ├── validator.py            # Defensive record validation engine
│   │   └── run_validation.py       # Validation runner with positive/negative test cases
│   ├── weather/
│   │   └── fetch_weather.py        # Timezone conversion and Open-Meteo weather enrichment
│   └── main.py                     # Unified CLI entry point for the pipeline
├── tests/
│   ├── test_db.py                  # Unit tests for database inserts and duplicate prevention
│   ├── test_parsers.py             # Unit tests for HTML parser error handling
│   └── test_validator.py           # Unit tests for game rules validation
├── pyproject.toml                  # Tooling and quality configuration
├── requirements.txt                # Python package dependencies
└── README.md                       # Project documentation and reproduction guide
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites & Virtual Environment

Ensure you have **Python 3.11+** installed.

```bash
# Clone the repository
git clone https://github.com/MohdRashid1607/ld-ml-02-lottery-pipeline.git
cd lottery-data-collector

# Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🛠️ Usage Instructions

### 1. Data Collection (Unified CLI)

Collect lottery draws using the centralized CLI entry point:

```bash
# View CLI options
python src/main.py --help

# Run full collection for EuroMillions
python src/main.py --game euromillions --mode full

# Run full collection for Thunderball
python src/main.py --game thunderball --mode full

# Run full collection for Set For Life
python src/main.py --game set_for_life --mode full

# Run incremental update (only fetches new draws newer than DB)
python src/main.py --game euromillions --mode incremental

# Fetch a custom range of draws
python src/main.py --game thunderball --start 3960 --end 3963
```

---

### 2. Meteorological & Weather Enrichment

Enrich all draws in SQLite with Paris & London historical temperatures at the draw timestamp:

```bash
python src/weather/fetch_weather.py
```

---

### 3. Launch the Interactive Data Explorer

Start the Streamlit dashboard:

```bash
streamlit run app/main.py
```

Features included in the web interface:
- **Search & Filter**: Filter by Game, City, Temperature Range, and Enrichment Status.
- **Detailed Inspector**: Inspect complete data lineage, coordinates, and weather match details per draw.
- **Visual Analytics**: Interactive ball frequency charts, temperature progression timelines, and venue distributions.
- **Data Export**: One-click download of the complete dataset in **CSV** (UTF-8) and **JSON** (ISO 8601) format.

---

### 4. Running Automated Tests & Quality Checks

```bash
# Run pytest test suite
python -m pytest tests/ -v

# Code formatting (Black)
black --check src/ tests/ app/

# Code linting (Ruff)
ruff check src/ tests/ app/
```

---

## 📊 Database Schema Summary

The SQLite database (`data/lottery.db`) is fully normalized:

- **`games`**: `game_id`, `name`
- **`venues`**: `venue_id`, `city`, `country_code`, `latitude`, `longitude`, `timezone`
- **`draws`**: `draw_id` (PK), `game_id`, `draw_number`, `draw_date`, `draw_local_datetime`, `draw_datetime_utc`, `venue_id`, `source_url`, `scraped_at`
- **`draw_numbers`**: `id` (PK), `draw_id`, `number_type` (`main` or `bonus`), `position`, `value`
- **`weather_readings`**: `draw_id` (PK), `provider`, `observed_at`, `temperature_c`, `match_minutes`, `status`

---

## ⚖️ Ethics & Responsible Use Statement

This repository is built solely for educational, research, and data engineering purposes under project **LD-ML-02**. Lottery draws are mathematically random, and all historical frequency and weather data are descriptive only and **do not predict future outcomes**. No automated ticket picking or gambling advice is provided.