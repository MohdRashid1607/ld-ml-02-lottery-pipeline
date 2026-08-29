# LLM Interaction & Prompt Engineering Log — LD-ML-02

Per the assignment guidelines, responsible AI usage requires transparent logging of prompts, model assistance, code modifications, and human verification.

| Day / Task | LLM Model | Purpose / Goal | Model Assistance Provided | Human Review & Modification | Verification Method |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Day 1–2** | Claude / ChatGPT | Project setup, source assessment, initial BS4 scraper | Generated boilerplate requests and BeautifulSoup selectors for EuroMillions | Verified CSS selectors against live DOM structure on national-lottery.co.uk | Tested extraction of 10 draws against browser results |
| **Day 3–4** | Antigravity / Claude | SQLite schema design, YAML validation rules | Suggested relational schema (`draws`, `draw_numbers`, `games`) and defensive validation | Enforced `UNIQUE (game_id, draw_number)` and added YAML config loader | Ran negative test cases (out-of-range balls, duplicate records) |
| **Day 5–6** | Antigravity / Claude | Full historical load & OOP refactoring | Abstracted `BaseCollector` and separated CLI arguments via `argparse` in `main.py` | Added rate-limiting delays and dynamic game registry | Executed `--mode full` and verified idempotence via duplicate counter |
| **Day 7–8** | Antigravity / Claude | Adding Thunderball & Set For Life collectors | Created `ThunderballCollector` and `SetForLifeCollector` subclasses | Fixed hardcoded `"lucky_stars"` in validator to dynamically pull bonus names | Generated 5-draw QA sheets and verified numbers visually against official website |
| **Day 9** | Antigravity | Automated pytest suite & PEP-8 formatting | Wrote test suite (`test_validator.py`, `test_parsers.py`, `test_db.py`) and audit script | Resolved mixed timezone warnings (`DTZ005`, `DTZ007`) to achieve clean Ruff output | Ran `pytest -v` (9/9 passed) and generated data quality audit report |
| **Day 10** | Antigravity | Weather enrichment & Streamlit Data Explorer | Built `fetch_weather.py` (Open-Meteo API) and full multi-tab Streamlit dashboard | Resolved Pandas mixed-timezone parsing and assigned unique Streamlit button keys | Tested live filters, temperature charts, and CSV/JSON export downloads |
