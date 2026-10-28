# Ethical and Responsible Data Use

## Data source, permissions, and attribution

This exercise accesses historical EPSS scores for three public vulnerability identifiers through FIRST.org's documented public API. FIRST makes EPSS data available without registration and requests attribution. The source is **FIRST.org EPSS**, with scores supplied by **Empirical Security**. See <https://www.first.org/epss/data> and <https://www.first.org/epss/faq>.

The API is designed for small lookups, not bulk harvesting. The notebook makes one narrowly scoped request, includes a timeout, and avoids aggressive parallel fetching. Researchers should check the provider's current terms and rate limits before reusing or expanding this workflow.

## Privacy and security

- Collected fields: CVE identifier, historical EPSS score, percentile, and score date.
- **No individual-level records, names, email addresses, credentials, IP addresses, or packet payloads** are intentionally requested or saved.
- No API key is required. The notebook does not ask reviewers to enter a GitHub personal access token.
- `.gitignore` excludes local outputs, `.env` files, common credentials files, and notebook checkpoints. This reduces accidental disclosure but cannot remove secrets previously committed; review commit history before publishing.
- Only source-controlled code and documentation should be pushed by default; derived output is stored locally for inspection. If sharing outputs later, confirm attribution and necessity.

## Fairness, interpretation, and limitations

- The three CVEs were chosen for a classroom demonstration. They are not randomly sampled and **do not represent all vulnerabilities**.
- EPSS is an estimate of likelihood of observed exploitation activity in a defined future window, not proof a particular system is vulnerable or compromised. It must not be treated as a complete risk metric.
- Model methodology and scores can change across EPSS versions; requests pinned to a date support comparison but do not guarantee permanent historical immutability.
- Possible misuse includes overstating risk, prioritizing security work solely by score, or presenting this small sample as a general evaluation. This notebook avoids those conclusions.
- Provider outages and historical data corrections remain external reproducibility constraints.

## Provenance and reproducibility safeguards

The notebook records the endpoint, fixed parameters, retrieval timestamp (UTC), Python version, returned row count, API version when provided, and SHA-256 hash of the sorted CSV. It validates scores and percentile ranges, duplicate IDs, returned score dates, and requested CVE IDs before saving.

## Academic integrity

This repository documents a learning exercise. Results are not invented: the notebook must execute successfully before claiming a retrieved sample. The source of the data, limitations, and distinctions from the separate NIDS research project are stated explicitly.
