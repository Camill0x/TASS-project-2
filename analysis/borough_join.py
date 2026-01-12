from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt

from config import AIRBNB_CLEAN, NYPD_CLEAN, DATA_DIR, PLOTS_DIR, ROOT_DIR
from features.crime_taxonomy import add_offense_group


BOROUGH_MAP = {
    "MANHATTAN": "Manhattan",
    "BROOKLYN": "Brooklyn",
    "QUEENS": "Queens",
    "BRONX": "Bronx",
    "STATEN ISLAND": "Staten Island",
}


def main() -> None:
    PLOTS_DIR.mkdir(exist_ok=True)

    print(f"Reading: {AIRBNB_CLEAN.relative_to(ROOT_DIR)}")
    airbnb = pd.read_csv(AIRBNB_CLEAN)

    print(f"Reading: {NYPD_CLEAN.relative_to(ROOT_DIR)}")
    nypd = pd.read_csv(NYPD_CLEAN)

    # Airbnb counts
    airbnb_b = (
        airbnb.groupby("neighbourhood_group")
        .agg(listings=("id", "count"),
             avg_price=("price", "mean"),
             median_price=("price", "median"))
        .reset_index()
        .rename(columns={"neighbourhood_group": "borough"})
    )

    # NYPD counts
    nypd["borough"] = nypd["borough"].astype(str).str.upper().str.strip()
    nypd = add_offense_group(nypd)

    nypd_b = (
        nypd.groupby("borough")
        .agg(
            crimes_total=("complaint_id", "count"),
            felonies=("law_category", lambda x: (x == "FELONY").sum()),
            misdemeanors=("law_category", lambda x: (x == "MISDEMEANOR").sum()),
            violations=("law_category", lambda x: (x == "VIOLATION").sum()),
            violent=("offense_group", lambda x: (x == "violent").sum()),
            property=("offense_group", lambda x: (x == "property").sum()),
        )
        .reset_index()
    )

    # Map NYPD borough labels to match Airbnb style
    nypd_b["borough"] = nypd_b["borough"].map(BOROUGH_MAP).fillna(nypd_b["borough"])

    merged = airbnb_b.merge(nypd_b, on="borough", how="left").sort_values("listings", ascending=False)

    out_csv = DATA_DIR / "borough_join_summary.csv"
    merged.to_csv(out_csv, index=False)
    print(f"Saved: {out_csv.relative_to(ROOT_DIR)}")
    print(merged)

    # Plot: listings vs crimes_total (2 separate bar charts for readability)
    plt.figure(figsize=(8, 4))
    plt.bar(merged["borough"], merged["listings"])
    plt.title("Airbnb listings by borough")
    plt.xticks(rotation=20)
    plt.tight_layout()
    out1 = PLOTS_DIR / "5-statistical" / "borough_airbnb_listings.png"
    plt.savefig(out1, dpi=200)
    plt.close()
    print(f"Saved: {out1.relative_to(ROOT_DIR)}")

    plt.figure(figsize=(8, 4))
    plt.bar(merged["borough"], merged["crimes_total"])
    plt.title("NYPD complaints (total) by borough (2018–2019)")
    plt.xticks(rotation=20)
    plt.tight_layout()
    out2 = PLOTS_DIR / "5-statistical" / "borough_crimes_total.png"
    plt.savefig(out2, dpi=200)
    plt.close()
    print(f"Saved: {out2.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
