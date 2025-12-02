import shutil
from pathlib import Path

import kagglehub

from config import (
    AIRBNB_KAGGLE_ID,
    AIRBNB_RAW,
    DATA_DIR,
    NYPD_KAGGLE_ID,
    NYPD_RAW,
    ROOT_DIR,
)


def download_from_kaggle(dataset_id: str, output_path: Path) -> None:
    """Download dataset via Kagglehub."""
    if output_path.exists():
        print(f"Skipping (already exists at {output_path.relative_to(ROOT_DIR)})")
        return

    print(f"Downloading dataset from Kaggle (id='{dataset_id}')...")

    dataset_path = Path(kagglehub.dataset_download(dataset_id))

    if not dataset_path.exists():
        raise RuntimeError(f"kagglehub download path does not exist: {dataset_path}")

    csv_files = list(dataset_path.glob("*.csv"))
    if not csv_files:
        raise RuntimeError(f"No CSV files found in Kaggle dataset at: {dataset_path}")

    if len(csv_files) > 1:
        print("Warning: multiple CSV files found, using the first one.")

    source_csv = csv_files[0]
    shutil.copy(source_csv, output_path)

    print(f"Saved dataset to: {output_path.relative_to(ROOT_DIR)} " f"(source: {source_csv.name})")


def main() -> None:
    """Download all required datasets from Kaggle."""
    DATA_DIR.mkdir(exist_ok=True)

    download_from_kaggle(AIRBNB_KAGGLE_ID, AIRBNB_RAW)
    download_from_kaggle(NYPD_KAGGLE_ID, NYPD_RAW)


if __name__ == "__main__":
    main()
