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

The datasets will be downloaded from the official University of Queensland repository. The original files will be stored in the `data/raw/` directory without modification.

The collection process will record the dataset name, version, download date, file size, and SHA-256 checksum.

### Data Validation

The following checks will be performed after loading the datasets:

| Validation Check | Purpose |
|---|---|
| File Availability | Confirm that the required dataset files exist |
| Dataset Dimensions | Record the number of rows and columns |
| Feature Names | Verify the presence of expected NetFlow features |
| Missing Values | Identify missing or null values |
| Duplicate Records | Identify duplicate network flow records |
| Class Distribution | Examine benign and malicious traffic proportions |
| Data Types | Check numerical and categorical columns |
| File Integrity | Calculate SHA-256 checksums |

The results of these checks will be recorded before preprocessing. Any changes made during preprocessing will be documented separately.

## 4. Collection Runs

A collection log will be maintained to record dataset downloads and validation activities.

| Run | Dataset | Download Date | Records Loaded | Validation Status |
|---|---|---|---|---|
| 1 | NF-CSE-CIC-IDS2018-v2 | Pending | Pending | Not executed |
| 2 | NF-UNSW-NB15-v2 | Pending | Pending | Not executed |
| 3 | NF-ToN-IoT-v2 (optional) | Pending | Pending | Not executed |
| 4 | NF-BoT-IoT-v2 (optional) | Pending | Pending | Not executed |

For each completed run, the file size, SHA-256 checksum, software environment, and any validation errors will also be recorded.

The collection log will be updated after the datasets have been downloaded and validated in Google Colab.
