# Data README and Provenance Log

## 1. Dataset Information

The project uses NetFlow Version 2 datasets provided by the University of Queensland. These datasets contain network flow records with 43 standardized NetFlow features and labels identifying benign and malicious traffic.

### Dataset Details

| Dataset | Usage | Published Records | Format |
|---|---|---:|---|
| NF-CSE-CIC-IDS2018-v2 | Primary | 18,893,708 | CSV |
| NF-UNSW-NB15-v2 | Primary | 2,390,275 | CSV |
| NF-ToN-IoT-v2 | Optional | 16,940,496 | CSV |
| NF-BoT-IoT-v2 | Optional | 37,763,497 | CSV |

### Data Characteristics

| Property | Description |
|---|---|
| Provider | University of Queensland |
| Dataset Version | NetFlow Version 2 |
| Data Type | Network flow records |
| Features | 43 NetFlow features |
| Labels | Benign and attack categories |
| File Format | CSV |
| Intended Task | Network intrusion detection |
| Dataset Access | Publicly available |

The published record counts are provided by the dataset authors. The actual number of records loaded and used in the experiments will be documented during implementation.




## 2. Data Dictionary

The NetFlow Version 2 datasets contain 43 network flow features and labels used to identify benign and malicious traffic.

| Feature / Column | Description |
|---|---|
| `IPV4_SRC_ADDR` | Source IPv4 address |
| `IPV4_DST_ADDR` | Destination IPv4 address |
| `L4_SRC_PORT` | Source port number |
| `L4_DST_PORT` | Destination port number |
| `PROTOCOL` | Network protocol identifier |
| `L7_PROTO` | Application-layer protocol |
| `IN_BYTES`, `OUT_BYTES` | Incoming and outgoing traffic in bytes |
| `IN_PKTS`, `OUT_PKTS` | Number of incoming and outgoing packets |
| `FLOW_DURATION_MILLISECONDS` | Duration of a network flow in milliseconds |
| `TCP_FLAGS` | TCP flag information |
| `MIN_TTL`, `MAX_TTL` | Minimum and maximum Time-to-Live values |
| `Label` | Binary classification: 0 = benign, 1 = malicious |
| `Attack` | Attack category associated with the network flow |

The table summarizes the main features and target columns. The complete 43-feature dictionary is available in the dataset documentation.

Feature reference: https://fkie-cad.github.io/COMIDDS/content/datasets/nf_uq_nids/


## 3. Data Collection and Validation

### Data Collection

The two primary datasets were downloaded from the University of Queensland and processed in Google Colab. The original CSV files were accessed from Google Drive without modifying them.

The notebook reads the datasets in chunks of 50,000 records and uses fixed random seeds to generate samples.

### Data Validation

The workflow checks dataset dimensions, feature names, class labels, missing values, class distributions, and file integrity.

Both complete primary datasets were successfully processed. No missing or invalid binary labels were found in the latest run.

Duplicate rows were identified in the generated samples: 2 in NF-CSE-CIC-IDS2018-v2 and 21 in NF-UNSW-NB15-v2. These counts were recorded without modifying the original data.

## 4. Collection Runs

Both primary datasets were processed in Google Colab on October 28, 2026.

| Dataset | Records Processed | Sampled Records | Status |
|---|---:|---:|---|
| NF-CSE-CIC-IDS2018-v2 | 18,893,708 | 4,000 | Passed |
| NF-UNSW-NB15-v2 | 2,390,275 | 4,000 | Passed |
| NF-ToN-IoT-v2 | Not processed | — | Optional |
| NF-BoT-IoT-v2 | Not processed | — | Optional |

A total of 8,000 records were sampled from the two primary datasets. The generated CSV files passed SHA-256 checksum verification.

The notebook records processing timestamps, source file checksums, sample checksums, software versions, and validation results in provenance files.

## 5. NVD API Collection

The notebook also collects a public vulnerability record from the NIST National Vulnerability Database using the NVD API.

An API key is stored securely in Google Colab Secrets and passed through the request header. The key is not included in the notebook or repository.

The API request successfully retrieved CVE-2021-44228.

| Item | Result |
|---|---|
| API | NVD CVE API 2.0 |
| CVE | CVE-2021-44228 |
| Records Collected | 1 |
| HTTP Status | 200 |
| Output | data/api/nvd_cve_example.csv |
| Provenance | data/api/nvd_cve_provenance.json |

The collected CSV has the following SHA-256 checksum:

`fc744b4ce7adadaf187f38e7103b2fe160edb0b5a472f0497134a1f875764be8`

The NVD record is collected separately and is not used as part of the network intrusion datasets.

Original datasets, generated samples, and local provenance files are not uploaded to GitHub.
Details are recorded in the notebook's generated provenance files.

