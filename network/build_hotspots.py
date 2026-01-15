from __future__ import annotations

import pandas as pd

from config import DATA_DIR, NYPD_CLEAN, ROOT_DIR
from features.crime_taxonomy import add_offense_group

GRID_SIZE = 0.005  # ~500 m


def main() -> None:
    print(f"Reading: {NYPD_CLEAN.relative_to(ROOT_DIR)}")
    df = pd.read_csv(NYPD_CLEAN)

    # Dodaj grupy violent/property/other
    df = add_offense_group(df)

    # Grid (zaokrąglanie współrzędnych)
    df["lat_cell"] = (df["latitude"] / GRID_SIZE).round() * GRID_SIZE
    df["lon_cell"] = (df["longitude"] / GRID_SIZE).round() * GRID_SIZE
    df["hotspot_id"] = df["lat_cell"].astype(str) + "_" + df["lon_cell"].astype(str)

    # Agregacja
    hotspots = (
        df.groupby(["hotspot_id", "lat_cell", "lon_cell"])
        .agg(
            total_crimes=("complaint_id", "count"),
            violent_crimes=("offense_group", lambda x: (x == "violent").sum()),
            felony_crimes=("law_category", lambda x: (x == "FELONY").sum()),
        )
        .reset_index()
    )

    out = DATA_DIR / "hotspots.csv"
    hotspots.to_csv(out, index=False)
    print(f"Saved hotspots: {out.relative_to(ROOT_DIR)}")
    print(f"Number of hotspots: {len(hotspots)}")


if __name__ == "__main__":
    main()
