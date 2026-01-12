from pathlib import Path

import pandas as pd

from config import (
    AIRBNB_CLEAN,
    AIRBNB_RAW,
    DATA_DIR,
    NYC_LAT_MAX,
    NYC_LAT_MIN,
    NYC_LON_MAX,
    NYC_LON_MIN,
    NYPD_CLEAN,
    NYPD_RAW,
    ROOT_DIR,
)


def validate_input_files(paths: list[Path]) -> None:
    """Check that all required raw files exist."""
    missing = [p for p in paths if not p.exists()]
    if missing:
        missing_str = ", ".join(str(p.relative_to(ROOT_DIR)) for p in missing)
        raise FileNotFoundError(f"Missing raw data files: {missing_str}")


def drop_missing_required(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Drop rows where any of the required columns are missing."""
    existing = [c for c in columns if c in df.columns]
    if not existing:
        return df
    return df.dropna(subset=existing)


def clean_airbnb() -> None:
    """Clean Airbnb NYC dataset and save a processed CSV file."""
    print(f"Reading Airbnb raw data from: {AIRBNB_RAW.relative_to(ROOT_DIR)}")
    df = pd.read_csv(AIRBNB_RAW)

    columns_to_keep = [
        "id",
        "name",
        "host_id",
        "host_name",
        "neighbourhood_group",
        "latitude",
        "longitude",
        "room_type",
        "price",
        "minimum_nights",
        "number_of_reviews",
        "last_review",
        "reviews_per_month",
        "availability_365",
    ]
    df = df[[col for col in columns_to_keep if col in df.columns]]

    # Drop rows where key descriptive columns are missing
    df = drop_missing_required(
        df,
        ["neighbourhood_group", "latitude", "longitude", "room_type", "price"],
    )

    # Filter coordinates that are clearly outside NYC bounds (rough filter)
    df = df[df["latitude"].between(NYC_LAT_MIN, NYC_LAT_MAX) & df["longitude"].between(NYC_LON_MIN, NYC_LON_MAX)]

    # Parse last_review as datetime
    df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")

    df.to_csv(AIRBNB_CLEAN, index=False)

    print(f"Saved cleaned Airbnb data to: {AIRBNB_CLEAN.relative_to(ROOT_DIR)}")


def clean_nypd() -> None:
    """Clean NYPD complaint dataset and save a processed CSV file."""
    print(f"Reading NYPD raw data from: {NYPD_RAW.relative_to(ROOT_DIR)}")
    df = pd.read_csv(NYPD_RAW)

    expected_columns = {
        "CMPLNT_NUM",
        "CMPLNT_FR_DT",
        "BORO_NM",
        "LAW_CAT_CD",
        "OFNS_DESC",
        "Latitude",
        "Longitude",
    }
    cols_present = [c for c in df.columns if c in expected_columns]
    df = df[cols_present]

    rename_map = {
        "CMPLNT_NUM": "complaint_id",
        "CMPLNT_FR_DT": "complaint_date",
        "BORO_NM": "borough",
        "LAW_CAT_CD": "law_category",
        "OFNS_DESC": "offense_description",
        "Latitude": "latitude",
        "Longitude": "longitude",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df["law_category"] = df["law_category"].astype(str).str.upper().str.strip()
    df["offense_description"] = df["offense_description"].astype(str).str.upper().str.strip()
    df["borough"] = df["borough"].astype(str).str.upper().str.strip()

    # Drop rows where key descriptive columns are missing
    df = drop_missing_required(
        df,
        ["complaint_date", "borough", "law_category", "offense_description", "latitude", "longitude"],
    )

    # Filter coordinates that are clearly outside NYC bounds (rough filter)
    df = df[df["latitude"].between(NYC_LAT_MIN, NYC_LAT_MAX) & df["longitude"].between(NYC_LON_MIN, NYC_LON_MAX)]

    # Drop rows where parsing failed (NaT)
    df = df.dropna(subset=["complaint_date"])

    # Parse complaint_date as datetime
    df["complaint_date"] = pd.to_datetime(df["complaint_date"], errors="coerce")

    # Keep only 2018–2019
    df = df[df["complaint_date"].dt.year.isin([2018, 2019])]

    df.to_csv(NYPD_CLEAN, index=False)

    print(f"Saved cleaned NYPD data to: {NYPD_CLEAN.relative_to(ROOT_DIR)}")


def main() -> None:
    """Clean all datasets used in the project."""
    DATA_DIR.mkdir(exist_ok=True)
    validate_input_files([AIRBNB_RAW, NYPD_RAW])

    clean_airbnb()
    clean_nypd()


if __name__ == "__main__":
    main()
