# TASS Project 2 - Airbnb & NYPD Analysis

A Python project for collecting, cleaning, and analyzing NYC Airbnb listings together with NYPD complaint records (2018-2019).
The goal is to build a unified dataset suitable for spatial analysis and further exploration.

## Environment setup

1. **Create and activate a Conda environment:**

   ```sh
   conda create -n tass python=3.12
   conda activate tass
   ```

2. **Install required dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Export the project root to `PYTHONPATH`:**

   From the root directory of the project:
   ```sh
   export PYTHONPATH=$(pwd)
   ```

## Download raw datasets

Airbnb (2019 snapshot) and NYPD historic complaint data (2006–2019) are downloaded directly from Kaggle using `kagglehub`.

To download both datasets, run:

```sh
python utils/download_datasets.py
```

Downloaded files will be placed in the `data/` directory.

## Clean datasets

To clean and filter the raw datasets including coordinate filtering and restricting NYPD data to 2018–2019, run:

```sh
python utils/clean_datasets.py
```

The cleaned versions will be saved as:

* `data/airbnb_clean.csv`
* `data/nypd_clean.csv`
