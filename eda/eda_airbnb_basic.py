import pandas as pd

from config import AIRBNB_CLEAN, ROOT_DIR


def main() -> None:
    print("=== Basic EDA - Airbnb dataset ===")
    print(f"Reading: {AIRBNB_CLEAN.relative_to(ROOT_DIR)}")

    df = pd.read_csv(AIRBNB_CLEAN)

    print("\n--- General info ---")
    print(f"Rows: {len(df)}")
    print("\nColumns:", ", ".join(df.columns))

    print("\n--- Price statistics ---")
    if "price" in df.columns:
        print(df["price"].describe())

    print("\n--- Listings per neighbourhood_group ---")
    if "neighbourhood_group" in df.columns:
        print(df["neighbourhood_group"].value_counts())

    print("\n--- Listings per room_type ---")
    if "room_type" in df.columns:
        print(df["room_type"].value_counts())

    print("\n--- Reviews per listing (describe) ---")
    if "number_of_reviews" in df.columns:
        print(df["number_of_reviews"].describe())

    print("\n--- Last review year counts ---")
    if "last_review" in df.columns:
        df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")
        years = df["last_review"].dt.year.value_counts().sort_index()
        print(years)


if __name__ == "__main__":
    main()
