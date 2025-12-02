import pandas as pd

from config import NYPD_CLEAN, ROOT_DIR


def main() -> None:
    print("=== Basic EDA - NYPD dataset ===")
    print(f"Reading: {NYPD_CLEAN.relative_to(ROOT_DIR)}")

    df = pd.read_csv(NYPD_CLEAN)

    print("\n--- General info ---")
    print(f"Rows: {len(df)}")
    print("\nColumns:", ", ".join(df.columns))

    print("\n--- Complaints per year ---")
    if "complaint_date" in df.columns:
        df["complaint_date"] = pd.to_datetime(df["complaint_date"], errors="coerce")
        year_counts = df["complaint_date"].dt.year.value_counts().sort_index()
        print(year_counts)

    print("\n--- Complaints per borough ---")
    if "borough" in df.columns:
        print(df["borough"].value_counts())

    print("\n--- Law category distribution ---")
    if "law_category" in df.columns:
        print(df["law_category"].value_counts())

    print("\n--- Top 10 offense types ---")
    if "offense_description" in df.columns:
        print(df["offense_description"].value_counts().head(10))


if __name__ == "__main__":
    main()
