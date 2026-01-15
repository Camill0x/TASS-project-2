from __future__ import annotations

import numpy as np
import pandas as pd

from config import AIRBNB_CLEAN, DATA_DIR, DEFAULT_RADIUS_M, NYPD_CLEAN, ROOT_DIR
from features.crime_taxonomy import add_offense_group

EARTH_RADIUS_M = 6371000.0


def add_grid_cell(df: pd.DataFrame, cell_size_m: int, lat0: float, lon0: float) -> pd.DataFrame:
    df = df.copy()

    lat = df["latitude"].to_numpy(dtype=float)
    lon = df["longitude"].to_numpy(dtype=float)

    lat0_rad = np.deg2rad(lat0)

    y = np.deg2rad(lat - lat0) * EARTH_RADIUS_M
    x = np.deg2rad(lon - lon0) * EARTH_RADIUS_M * np.cos(lat0_rad)

    y_bin = np.floor_divide(y.astype(np.int64), cell_size_m).astype(np.int64)
    x_bin = np.floor_divide(x.astype(np.int64), cell_size_m).astype(np.int64)

    df["cell_y_bin"] = y_bin
    df["cell_x_bin"] = x_bin
    df["cell_id"] = y_bin.astype(str) + "_" + x_bin.astype(str)

    return df


def make_grid_counts(airbnb: pd.DataFrame, nypd: pd.DataFrame, cell_size_m: int) -> pd.DataFrame:
    lat0 = float(pd.concat([airbnb["latitude"], nypd["latitude"]], ignore_index=True).mean())
    lon0 = float(pd.concat([airbnb["longitude"], nypd["longitude"]], ignore_index=True).mean())

    a = add_grid_cell(airbnb, cell_size_m, lat0, lon0)
    c = add_grid_cell(nypd, cell_size_m, lat0, lon0)

    airbnb_counts = a.groupby("cell_id").size().rename("airbnb_count").reset_index()
    nypd_counts = c.groupby("cell_id").size().rename("nypd_count").reset_index()

    out = airbnb_counts.merge(nypd_counts, on="cell_id", how="outer")

    if "law_category" in c.columns:
        law = (
            c.pivot_table(index="cell_id", columns="law_category", aggfunc="size", fill_value=0)
            .rename(columns=lambda x: str(x).strip().lower())
            .reset_index()
        )
        out = out.merge(law, on="cell_id", how="left")

    if "offense_group" in c.columns:
        grp = (
            c.pivot_table(index="cell_id", columns="offense_group", aggfunc="size", fill_value=0)
            .rename(columns=lambda x: f"{str(x).strip()}_count")
            .reset_index()
        )
        out = out.merge(grp, on="cell_id", how="left")

    out = out.fillna(0)

    count_cols = [c for c in out.columns if c != "cell_id"]
    out[count_cols] = out[count_cols].astype(np.int64)

    return out


def main() -> None:
    cell_size_m = DEFAULT_RADIUS_M

    print(f"Reading: {AIRBNB_CLEAN.relative_to(ROOT_DIR)}")
    airbnb = pd.read_csv(AIRBNB_CLEAN)

    print(f"Reading: {NYPD_CLEAN.relative_to(ROOT_DIR)}")
    nypd = pd.read_csv(NYPD_CLEAN)

    required = ["latitude", "longitude"]
    for name, df in [("airbnb", airbnb), ("nypd", nypd)]:
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns in {name}: {missing}")

    if "law_category" in nypd.columns:
        nypd["law_category"] = nypd["law_category"].astype(str).str.upper().str.strip()

    if "offense_description" in nypd.columns:
        nypd["offense_description"] = nypd["offense_description"].astype(str).str.upper().str.strip()

    if "offense_group" not in nypd.columns and "offense_description" in nypd.columns:
        nypd = add_offense_group(nypd)

    grid = make_grid_counts(airbnb, nypd, cell_size_m)

    out_path = DATA_DIR / f"grid_counts_{cell_size_m}m.csv"
    grid.to_csv(out_path, index=False)

    print(f"Saved: {out_path.relative_to(ROOT_DIR)}")
    print(f"Rows (cells): {len(grid)}")
    print("Columns:", ", ".join(grid.columns))


if __name__ == "__main__":
    main()
