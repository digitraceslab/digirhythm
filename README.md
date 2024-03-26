
# Digi Rhythm: inferring daily rhythm from digital traces

## Description
Placeholer for short description

Project Organization
------------

    ├── README.md          <- The top-level README for developers using this project.
    │    
    ├── run.sh          <- Scripts to produce the data and generate similarity matrix
    ├── data
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │
    │
    ├── analysis          <- Jupyter notebooks.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── features       
    │   │
    │   │   └── corona     <- Process script for corona study
    │   │   └────── vectorize_corona.py    <- Combine individual sensors into one vector
    │   │
    │   │   └── momomood     <- Process script for momomood study
    │   │   └────── vectorize_momo    <- Combine individual sensors into one vector
    │   │
    │   │   └── baseline_rhythm.py     <- Computing baseline behaviour with different strategies
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io

--------


## Setup

### Requirements
Requires Python 3.10 or higher.
Install requirements:
`python3 -m pip install -r requirements.txt`

### Config file

Paths in config file are placeholder. Replace with the actual paths to the data...
Copy `config/paths/config.ini.sample` as `config/paths/config.ini` and replace the paths accordingly

# MoMoMood Data Analysis Pipeline

This section provides instructions for executing the data analysis pipeline for the MoMoMood project, which includes processing sensor data, vectorizing features, and computing similarity matrices. Additionally, a utility script for folder backup is also provided.

## Analysis Pipeline

Follow these steps to process the data and generate insights:

### 1. Process Sensor Data

Process the sensor data at a predetermined frequency. This step involves running a sensor processor with specified sensor types (e.g., call) and frequencies (e.g., 4epochs).

```bash
python3 -m src.features.momomood.sensors.run_processor processor.sensor=call processor.frequency=4epochs
```

Replace `processor.sensor=call` with the sensor you want to process (e.g., `sms`, `location`) and `processor.frequency=4epochs` with the desired frequency (e.g., `7ds`, `14ds`).

### 2. Vectorize Features

After processing the sensor data, the next step is to vectorize the features to prepare them for analysis.

```bash
python3 -m src.features.momomood.vectorize_momo
```

This command vectorizes the processed data, transforming it into a format suitable for further analysis.

### 3. Compute Similarity Matrix

The final step in the analysis pipeline is to compute the similarity matrix. This matrix helps in understanding the relationships and similarities between different data points.

```bash
python3 -m src.features.similarity_matrix
```

This command calculates the similarity matrix based on the vectorized data.

## Utility Script

### Folder Backup

It's essential to regularly back up your data to prevent loss. Use the following `rsync` command to backup the data folder:

```bash
rsync -av --progress --delete data/ data.backup
```

---

For any additional information or troubleshooting, refer to the specific documentation of each module or contact the project maintainers.
--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
