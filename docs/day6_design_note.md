# Day 6 — Design Note: Refactoring into a Reusable Collector

## Engineering Principles Applied

### 1. Single Responsibility
Each file now has exactly one job:
- `base.py` — HTTP fetching and retry logic only
- `euromillions.py` — EuroMillions HTML parsing only
- `validator.py` — validation rules only
- `db.py` — database operations only
- `main.py` — CLI argument handling and orchestration only

### 2. DRY (Don't Repeat Yourself)
Before Day 6, retry logic and headers were duplicated across scripts.
Now all collectors share one `BaseCollector.fetch_draw_page()` method.
Adding a new game means zero duplication of HTTP logic.

### 3. Configuration over Constants
All game rules (number ranges, ball counts, source URLs) live in
`config/game_rules.yaml`. All scripts read from there via `config/settings.py`.
No hardcoded numbers in Python files.

### 4. KISS (Keep It Simple)
We used Python's `abc.ABC` / `@abstractmethod` to enforce the interface.
Adding a new game only requires 3 steps:
1. Add its config to `game_rules.yaml`
2. Create a subclass of `BaseCollector` with `parse_html()`
3. Register it in `COLLECTOR_REGISTRY` in `main.py`

### 5. Dependency Injection
`EuroMillionsCollector` receives its `config` dict at construction time
rather than loading it internally. This makes it testable in isolation.

### 6. Improved CLI (argparse)
`main.py` replaces all old one-off scripts with a single unified
command supporting `--game`, `--mode`, `--start`, `--end`, and `--db`.