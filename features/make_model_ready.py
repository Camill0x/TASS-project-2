from __future__ import annotations

import numpy as np
import pandas as pd

from config import AIRBNB_CLEAN, DATA_DIR, ROOT_DIR


def main() -> None:
    print(f"Reading: {AIRBNB_CLEAN.relative_to(ROOT_DIR)}")
    df = pd.read_csv(AIRBNB_CLEAN)

    # --- Basic sanity ---
    if "price" not in df.columns:
        raise ValueError("Missing 'price' column in Airbnb data")

    # Fill reviews_per_month for modelling convenience
    if "reviews_per_month" in df.columns:
        df["reviews_per_month"] = df["reviews_per_month"].fillna(0)

    # Optional: remove obviously invalid/degenerate prices
    # (Kaggle dataset sometimes contains 0)
    df = df[df["price"].notna()]
    df = df[df["price"] >= 10]

    # Cut extreme outliers for stats/models (keep clean dataset intact!)
    df = df[df["price"] <= 1000]

    # log-price for regression
    df["log_price"] = np.log1p(df["price"])

    out_path = DATA_DIR / "airbnb_model.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved model-ready Airbnb to: {out_path.relative_to(ROOT_DIR)}")
    print(f"Rows: {len(df)}")


if __name__ == "__main__":
    main()
