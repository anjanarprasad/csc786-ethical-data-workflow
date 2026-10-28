# Data README and Provenance Log

## Dataset

**Provider:** FIRST.org Exploit Prediction Scoring System (EPSS); scores provided by Empirical Security.  
**API endpoint:** <https://api.first.org/data/v1/epss>  
**API documentation:** <https://api.first.org/epss/>  
**Date of historical scores requested:** `2024-06-01`  
**CVE parameters:** `CVE-2021-44228,CVE-2023-34362,CVE-2023-44487`  
**Output location:** `data/epss_2024-06-01.csv` (ignored by Git by default)

### Data dictionary

| Column | Definition |
|---|---|
| `cve` | Public CVE identifier |
| `epss` | EPSS probability estimate in [0, 1], recorded to nine decimal places |
| `percentile` | EPSS percentile in [0, 1], recorded to nine decimal places |
| `date` | Historical score date, ISO `YYYY-MM-DD` |

Rows are sorted by `cve` and stored with a fixed column order and Unix-style newlines, making cross-run SHA-256 comparisons meaningful. The run-specific UTC retrieval time is stored **outside** the CSV.

### Collection and validation

- HTTPS GET, one small batch, no API key required.
- HTTP errors are not silently ignored. No example data is substituted for a failed live request.
- Each response is validated for correct CVEs, date, numeric ranges, and duplicate identifiers.
- The notebook writes `data/provenance.json` for the latest run and appends a Markdown entry below (if this file is available in the working directory).
- No live collection is pre-claimed in this template; the log below is populated when a reviewer runs the notebook.

## Collection runs

<!-- New runs appended below by the notebook. -->
