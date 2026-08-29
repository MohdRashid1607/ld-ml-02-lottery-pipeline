# Location & Weather Assessment — LD-ML-02

## 1. Official Draw Venues & Scheduled Times

| Game | Official Draw City | Venue / Studio Details | Scheduled Local Time | IANA Timezone | Coordinates (Lat, Lon) | Evidence & Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EuroMillions** | **Paris, France** | FDJ (Française des Jeux) Studios, Paris | 21:00 CET / CEST | `Europe/Paris` | `48.8566, 2.3522` | Official European coordinating draw center for all 9 participating countries. |
| **Thunderball** | **London, United Kingdom** | Allwyn / BBC Broadcast Studios, London | 20:00 GMT / BST | `Europe/London` | `51.5074, -0.1278` | Official National Lottery draw studio location in Greater London. |
| **Set For Life** | **London, United Kingdom** | Allwyn / National Lottery Broadcast HQ, London | 20:00 GMT / BST | `Europe/London` | `51.5074, -0.1278` | Official draw studio location for UK National Lottery games. |

---

## 2. Weather Provider Evaluation

We evaluated candidate meteorological APIs for historical air temperature enrichment:

| Provider | Historical Coverage | Resolution | Pricing / Rate Limits | Licensing & Attribution | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Open-Meteo Historical Archive** | 1940 to present | Hourly | Free (up to 10,000 calls/day), no API key needed | Non-commercial open data (Attribution required: Open-Meteo) | **Selected** |
| **Visual Crossing** | 1970 to present | Hourly | Limited free tier (1,000 records/day) | Proprietary, key required | Rejected (rate limits too strict) |
| **Meteostat** | 1990 to present | Hourly | Open source, station-based | Requires station mapping | Rejected (complex setup) |

---

## 3. Matching Methodology & Timezone Normalization

1. **Local to UTC Conversion**: 
   - Uses Python's `zoneinfo` with IANA timezone database (`Europe/Paris`, `Europe/London`).
   - Automatically handles Daylight Saving Time (DST) transitions (CET/CEST and GMT/BST).
2. **Nearest Hour Matching**:
   - Compares UTC draw timestamp against hourly reanalysis model output from Open-Meteo (`temperature_2m`).
   - Maximum permitted difference: 60 minutes.
   - Status flag set to `verified` for direct hourly matches.
3. **Unit Consistency**:
   - All temperatures are strictly stored and exported in **Degrees Celsius (°C)**.
