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

The two primary datasets, NF-CSE-CIC-IDS2018-v2 and NF-UNSW-NB15-v2, were downloaded from the University of Queensland and processed using Google Colab.

The original CSV files were stored in the `data/raw/` directory without modification. The notebook used a fixed random seed to generate reproducible samples.

### Data Validation

The notebook was executed with both primary datasets. The validation process included checking dataset features, class labels, missing values, and generating samples.

| Validation Check | Purpose |
|---|---|
| File Availability | Confirm that the required CSV files exist |
| Dataset Dimensions | Record the number of rows and columns |
| Feature Names | Verify the expected NetFlow features |
| Missing Labels | Identify records without valid classification labels |
| Class Distribution | Examine benign and malicious traffic proportions |
| Sampling | Generate reproducible samples using a fixed random seed |
| File Integrity | Verify saved files using SHA-256 checksums |

During validation, one record with a missing binary label was identified in NF-CSE-CIC-IDS2018-v2. The notebook was updated to exclude records with missing labels from the processed data while preserving the original dataset.

## 4. Collection Runs

Both primary datasets were processed and verified in Google Colab on October 28, 2026.

| Dataset | Sampled Records | Validation Status |
|---|---:|---|
| NF-CSE-CIC-IDS2018-v2 | 4,000 | Passed |
| NF-UNSW-NB15-v2 | 4,000 | Passed |
| NF-ToN-IoT-v2 (optional) | Not processed | Not executed |
| NF-BoT-IoT-v2 (optional) | Not processed | Not executed |

The notebook successfully generated 4,000 sampled records from each primary dataset, giving a total of 8,000 sampled records.

The saved sampled files passed SHA-256 checksum verification. The original datasets and generated data files will not be uploaded to the public GitHub repository.

The actual checksums, software versions, and additional validation details are recorded in the notebook's generated provenance files.

