# Day 9 - Data Quality Audit Report

## Total Records per Game
- euromillions: 50 draws
- set_for_life: 33 draws
- thunderball: 81 draws


## Null Checks
- Draws with null required fields: 0 ✅

## Duplicate Checks
- Duplicate draws (same game & draw number): 0 ✅

## Number Counts Checks
- EuroMillions draws with wrong ball counts: 0 ✅
- Thunderball draws with wrong ball counts: 0 ✅
- Set For Life draws with wrong ball counts: 0 ✅

## Known Limitations
- **Date Gaps**: Some draws may appear missing if the official site returns a 404 for specific draw numbers. The incremental collector handles this gracefully by skipping invalid URLs.
- **Historical Backfill**: The official site only allows fetching the most recent ~180 days for Thunderball and Set For Life. Deeper backfill would require CSV ingestion.