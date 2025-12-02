from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

DATA_DIR = ROOT_DIR / "data"

NYPD_KAGGLE_ID = "brunacmendes/nypd-complaint-data-historic-20062019"
AIRBNB_KAGGLE_ID = "dgomonov/new-york-city-airbnb-open-data"

NYPD_RAW = DATA_DIR / "nypd.csv"
AIRBNB_RAW = DATA_DIR / "airbnb.csv"

NYPD_CLEAN = DATA_DIR / "nypd_clean.csv"
AIRBNB_CLEAN = DATA_DIR / "airbnb_clean.csv"

NYC_LAT_MIN, NYC_LAT_MAX = 40.49, 40.92
NYC_LON_MIN, NYC_LON_MAX = -74.26, -73.70
