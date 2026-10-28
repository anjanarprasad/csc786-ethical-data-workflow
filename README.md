# CSC 786 — Ethical Data Collection and Reproducibility

## Purpose

This small, reproducible cybersecurity data-collection exercise retrieves **historical Exploit Prediction Scoring System (EPSS)** values for three public CVE identifiers from **FIRST.org**. It demonstrates ethical use of a public API, documented collection parameters, local file storage, cryptographic checksums, and data provenance logging.

**Scope:** This is a **Module 5 data ethics/reproducibility demonstration**, not the training or evaluation dataset for the separate Network Intrusion Detection System (NIDS) course project. EPSS scores are vulnerability-level statistics, not network traffic records.

## Data source and citation

- Data provider: FIRST.org EPSS Special Interest Group; data provided by Empirical Security.
- Endpoint: <https://api.first.org/data/v1/epss>
- Documentation: <https://api.first.org/epss/>
- Data and attribution: <https://www.first.org/epss/data>
- FAQ and interpretation: <https://www.first.org/epss/faq>
- Access: Public; no API key or account needed; EPSS requests for small CVE batches are an intended API use case.

Please credit FIRST.org and Empirical Security when reusing scores. This repository contains only a narrow API query, not a bulk redistribution of EPSS data.

## Fixed collection parameters

| Parameter | Value |
|---|---|
| Endpoint | `https://api.first.org/data/v1/epss` |
| Method | `GET` |
| `cve` | `CVE-2021-44228,CVE-2023-34362,CVE-2023-44487` |
| `date` | `2024-06-01` |
| Requested fields | CVE ID, EPSS score, percentile, score date |
| Expected scope | Up to three CVE records, not a representative cybersecurity sample |
| Output | `data/epss_2024-06-01.csv` and `data/provenance.json` |

Using a fixed historical score date avoids normal day-to-day changes in *current* EPSS scores. Reproducibility still depends on continued API availability and whether the provider revises historical results.

## Repository contents

| File or folder | Purpose |
|---|---|
| `notebooks/CSC786_Ethical_Data_Workflow.ipynb` | Main Colab notebook: fetch, validate, save, log, verify |
| `README.md` | Purpose, sources, setup, reproduction instructions |
| `ETHICS.md` | Privacy, attribution, rate limits, security, bias, and limitations |
| `DATA_README.md` | Data dictionary, collection configuration, provenance log |
| `.gitignore` | Excludes local data outputs and secrets |
| `requirements.txt` | Dependency note (Python standard library only) |
| `tests/test_notebook_workflow.py` | Offline smoke tests, no API access required |
| `data/.gitkeep` | Keeps the output folder in the repository |

## How to reproduce in Google Colab

1. Open a **new Colab notebook** at <https://colab.research.google.com/>.
2. Clone the public GitHub repository and move into it (replace the placeholders):

   ```python
   !git clone https://github.com/YOUR_GITHUB_USERNAME/csc786-ethical-data-workflow.git
   %cd csc786-ethical-data-workflow
   !ls -la
   ```

3. In Colab's **Files** sidebar, locate `notebooks/CSC786_Ethical_Data_Workflow.ipynb` and open it (or open the notebook directly from the repository through Colab's GitHub tab). Run **Runtime > Run all**. The notebook uses the current working directory; if the cloned folder is not the current directory, it will print where outputs are written.
4. A successful network request generates `data/epss_2024-06-01.csv`, `data/provenance.json`, and an appended provenance entry in `DATA_README.md` in the current working directory. Inspect the displayed row count and checksum.
5. To run the independent offline validation tests from the repository directory:

   ```python
   !python -m unittest discover -s tests -v
   ```

6. Rerun the notebook with the same date and CVEs. Compare the **SHA-256 CSV hash** across runs. The retrieval timestamp and `DATA_README.md` run-log entry will change, but the CSV hash should stay the same unless the provider changes historical values.

**Colab note:** When you open an `.ipynb` from GitHub, Colab may begin in `/content` rather than the cloned folder. For the easiest run, first clone and `%cd` to the repository in the same runtime, or accept that outputs are saved under `/content/data`. There are **no hard-coded personal paths**.

## Troubleshooting

- `HTTP Error 429`: Too many requests. Stop repeated polling and retry later; the workflow only needs one request per run.
- Connection/timeout error: Verify network access and the API's status; no valid outputs should be claimed if the request failed.
- `ValueError` during validation: The API schema or historical data may have changed; inspect the returned response and document the change before modifying the parser.
- Missing `data/`: The notebook creates it automatically.
- GitHub push: Data output files and secrets are excluded by `.gitignore`. Upload the source notebook and Markdown files, not access tokens or unnecessary raw API dumps.

## Expected results and limitations

The notebook should print the queried score date, the number of returned CVEs, where it saved the CSV and metadata, and the file's SHA-256 hash. The repository **does not claim that a live API request was successfully executed before publication**. Reviewers should run the notebook and report their actual results. The three selected CVEs are an illustrative convenience sample; EPSS is a predictive score, not proof of exploitation or a stand-alone vulnerability risk decision.

## Original workshop reference

Structure adapted for the Module 5 assignment using the instructor's `CSC786_Ethics_Demo_ST.ipynb` as a learning reference. No GitHub tokens, account information, or personal paths from the workshop notebook were reused.
