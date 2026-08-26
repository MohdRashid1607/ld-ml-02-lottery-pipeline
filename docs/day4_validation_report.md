code : 
python src\validation\run_validation.py

output: 
(venv) C:\Users\hp\Documents\GitHub\lottery-data-collector>python src\validation\run_validation.py
Collecting real EuroMillions draws (1965-1974)...
Fetching draw 1965...
Fetching draw 1966...
Fetching draw 1967...
Fetching draw 1968...
Fetching draw 1969...
Fetching draw 1970...
Fetching draw 1971...
Fetching draw 1972...
Fetching draw 1973...
Fetching draw 1974...
Collected 10 real records.
Validating 15 records (10 real + 5 deliberately invalid)...

============================================================
VALIDATION SUMMARY
============================================================
Passed: 10
Failed: 5

Rejected records and reasons:

  BAD-1-OUT-OF-RANGE:
    - Main numbers out of range [1-50]: [51]

  BAD-2-WRONG-COUNT:
    - Expected 5 main numbers, got 4

  BAD-3-DUPLICATE:
    - Main numbers contain duplicates: [2, 2, 8, 28, 39]

  BAD-4-BAD-DATE:
    - Invalid date format: '2026-07-21' (expected format like '%a %d %b %Y')

  BAD-5-MISSING-FIELD:
    - Missing required field: draw_date

(venv) C:\Users\hp\Documents\GitHub\lottery-data-collector>