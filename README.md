# CSC 786 — Ethical Data Collection and Reproducibility

## Project Purpose

This project aims to evaluate the robustness and computational efficiency of machine learning-based Network Intrusion Detection Systems (NIDS) under distribution shifts. It will explore how models trained on one network intrusion dataset will perform when tested on a different dataset. It will also look at the impact of compression techniques on the detection accuracy, false-positive rate and efficiency of the models.

**Scope:** The project will be carried out in a controlled experimental setting. There will be no live network traffic collection, real-time intrusion detection, or deployment in a real-world environment. The project will be limited to specific datasets, ML models, and compression methods.
### Data Sources

The project will use publicly available NetFlow-based network intrusion datasets from the University of Queensland (UQ). The following datasets have been selected:

#### Primary Datasets

1. **NF-CSE-CIC-IDS2018-v2**
   - [Dataset Download](https://rdm.uq.edu.au/files/ce5161d0-ef9c-11ed-827d-e762de186848)

2. **NF-UNSW-NB15-v2**
   - [Dataset Download](https://rdm.uq.edu.au/files/8c6e2a00-ef9c-11ed-827d-e762de186848)

#### Additional Datasets (if computational resources permit)

3. **NF-ToN-IoT-v2**
   - [Dataset Download](https://rdm.uq.edu.au/files/a4ad7080-ef9c-11ed-a964-b70596e96ad5)

4. **NF-BoT-IoT-v2**
   - [Dataset Download](https://rdm.uq.edu.au/files/b97fa3c0-ef9c-11ed-8007-832d3bc76ba8)

**Official Dataset Website:** https://staff.itee.uq.edu.au/marius/NIDS_datasets/

All four datasets use a common set of 43 NetFlow features, which supports cross-dataset evaluation.

Dataset Licensing and Usage

According to the University of Queensland, the datasets can be used for academic research purposes provided that the relevant research papers are cited. Commercial use requires agreement with the dataset authors.

The original datasets will not be redistributed through this GitHub repository. Links to the original sources are provided instead.

Official Dataset Website: https://staff.itee.uq.edu.au/marius/NIDS_datasets/

Licence Information: https://www.cyber.uq.edu.au/project/machine-learning-based-nids-datasets

Dataset Reference

Sarhan, M., Layeghy, S., & Portmann, M. (2022). Towards a Standard Feature Set for Network Intrusion Detection System Datasets. Mobile Networks and Applications.

https://doi.org/10.1007/s11036-021-01843-0

### Fixed Collection Parameters

| Parameter | Value |
|---|---|
| Primary Datasets | NF-CSE-CIC-IDS2018-v2, NF-UNSW-NB15-v2 |
| Additional Datasets | NF-ToN-IoT-v2, NF-BoT-IoT-v2 (optional) |
| Dataset Version | Version 2 (v2) |
| Data Format | CSV |
| Features | 43 standardized NetFlow features |
| Target Labels | Benign and malicious traffic |
| Collection Method | Download from the official University of Queensland repository |
| Collection Date | Recorded at the time of download |
| Data Integrity | SHA-256 checksum and file size verification |
| Original Data | Preserved without modification |
| Sampling Method | Seeded random sampling, up to 2,000 records per binary class per dataset |
| Random Seed | 42 for NF-CSE-CIC-IDS2018-v2; 43 for NF-UNSW-NB15-v2 |
| Chunk Size | 50,000 records |

The original datasets will be preserved without modification. Any sampling or preprocessing steps will be documented separately to ensure reproducibility.


### Repository Structure

| File or Folder | Purpose |
|---|---|
| CSC786_NIDS_Reproducible_Colab.ipynb` | Main Colab notebook for NIDS data validation, sampling, and NVD API collection |
| `README.md` | Project purpose, scope, data sources, setup, and reproducibility instructions |
| `ETHICS.md` | Privacy, dataset licensing, ethical considerations, and limitations |
| `DATA_README.md` | Dataset details, preprocessing parameters, and data provenance |
| `.gitignore` | Excludes large datasets, temporary files, and sensitive information |
| `requirements.txt` | Python dependencies required to run the notebook |



## How to Reproduce in Google Colab

1. Open Google Colab and select the GitHub option under File > Open notebook.

2. Enter the repository URL:
   https://github.com/anjanarprasad/csc786-ethical-data-workflow

3. Open `CSC786_NIDS_Reproducible_Colab.ipynb`.

4. Download the two primary CSV datasets using the official University of Queensland links provided above.

5. Store the CSV files in a folder in your own Google Drive. Run the setup cell and enter that folder's path relative to My Drive when prompted. Alternatively, place the CSV files in the repository's `data/raw/` folder.

6. Run the remaining cells to validate the datasets, generate samples, and save the provenance records.

7. For the NVD API section, request a free API key from:
   https://nvd.nist.gov/developers/request-an-api-key

   Save the key as `NVD_API_KEY` in Colab Secrets and enable notebook access. The API section can be skipped if no key is available.

8. Check the output files and SHA-256 verification results.

The original datasets and API keys are not included in this repository. Reviewers must obtain their own copies and credentials.

This product uses the NVD API but is not endorsed or certified by the NVD.

## Troubleshooting

- **FileNotFoundError:** Check whether the datasets have been downloaded, extracted, and placed in the correct `data/raw/` directory.
- **ModuleNotFoundError:** Install the missing dependencies using `!pip install -r requirements.txt`.
- **Memory Error:** Large datasets may exceed Google Colab's available memory. Use a documented sampling method if necessary.
- **Missing or Mismatched Features:** Verify that the correct dataset versions are being used and check the feature names before preprocessing.
- **Missing data folder:** Create the required directories before saving the processed files.
- **GitHub Upload:** Avoid uploading large original datasets, sensitive information, or unnecessary output files. Use `.gitignore` to exclude them.

## Expected Results and Limitations

The notebook is intended to load and validate the selected network intrusion datasets. It should display the number of records, features, missing values, and class distributions. Any preprocessing steps and generated outputs should be documented to support reproducibility.

The project uses publicly available datasets and does not involve collecting live network traffic. Computational resources may limit the amount of data that can be processed in Google Colab.

The data preparation workflow does not represent the complete NIDS implementation or its final evaluation results.

