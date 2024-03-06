
# Digi Rhythm: inferring daily rhythm from digital traces

Project Organization
------------

    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── corona     <- Process script for corona study
    │   │   └── momomood     <- Process script for momomood study
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io

--------
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

It's essential to regularly back up your data to prevent loss. Use the following `rsync` command to backup your data folder:

```bash
rsync -av --progress --delete data/ data.backup
```

This command synchronizes the contents of the `data/` folder with `data.backup/`, ensuring that you have a current backup. The `--delete` flag ensures that files deleted from `data/` are also removed from `data.backup/` to keep the backup folder clean and consistent with the source.

---

For any additional information or troubleshooting, refer to the specific documentation of each module or contact the project maintainers.
--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
