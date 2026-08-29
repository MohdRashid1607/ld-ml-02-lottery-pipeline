# Source Assessment — LD-ML-02

## Purpose
Compare candidate official sources for EuroMillions, UK Lotto/Thunderball, and Set For Life
before starting data collection, as required by Day 1 of the assignment.

## Candidate Sources

### 1. national-lottery.co.uk (Official UK National Lottery site)
- Games covered: UK Lotto, Thunderball, Set For Life, EuroMillions (UK draws)
- Format: HTML only, no public API
- Historical coverage: Full draw history per game, browsable by date/year
- Update frequency: Updated shortly after each draw
- Access restrictions: No public API; must respect robots.txt and reasonable
  request rates. No CAPTCHA observed on results pages.

### 2. euro-millions.com (Official EuroMillions results site)
- Games covered: EuroMillions only
- Format: HTML only, no public API
- Historical coverage: Full EuroMillions draw history
- Update frequency: Updated shortly after each draw
- Access restrictions: No public API; standard scraping etiquette applies.

## Comparison Summary

| Source                 | Games covered            | Format | API? | Notes                              |
|-------------------------|---------------------------|--------|------|-------------------------------------|
| national-lottery.co.uk  | All 3 target games         | HTML   | No   | One consistent page structure covers all target games |
| euro-millions.com       | EuroMillions only          | HTML   | No   | Single-game only, less reusable    |

## Decision

**Selected first game: EuroMillions**
**Selected source: national-lottery.co.uk**

Reasoning: national-lottery.co.uk hosts EuroMillions, UK Lotto/Thunderball, and Set For Life
under the same site and page structure. Building the collector and parser for EuroMillions
first means the same approach (with configuration changes only — URLs and number ranges)
should generalize to the other two target games in later days, satisfying the requirement to
build one game first and expand only after approval.

## Access Notes
- No API keys or authentication required.
- robots.txt to be checked before first request in Day 2.
- Access date will be recorded per request in code logs, not in this document.