from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

from config import AIRBNB_CLEAN, DATA_DIR, NYPD_CLEAN, ROOT_DIR
from features.crime_taxonomy import add_offense_group

EARTH_RADIUS_M = 6371000.0


def to_radians(df: pd.DataFrame) -> np.ndarray:
    return np.deg2rad(df[["latitude", "longitude"]].to_numpy(dtype=float))


def counts_for_radius(airbnb: pd.DataFrame, nypd: pd.DataFrame, radius_m: float) -> pd.DataFrame:
    """
    Dla każdej oferty Airbnb liczy liczbę przestępstw w promieniu radius_m
    + rozbicie na law_category oraz offense_group (violent/property/other).
    """
    radius_rad = radius_m / EARTH_RADIUS_M

    airbnb_rad = to_radians(airbnb)
    nypd_rad = to_radians(nypd)

    tree = BallTree(nypd_rad, metric="haversine")
    idx = tree.query_radius(airbnb_rad, r=radius_rad)

    # numpy arrays for fast counting
    law = nypd["law_category"].astype(str).str.upper().to_numpy()
    grp = nypd["offense_group"].astype(str).to_numpy()

    total = np.fromiter((len(i) for i in idx), dtype=int)
    fel = np.fromiter((np.sum(law[i] == "FELONY") for i in idx), dtype=int)
    mis = np.fromiter((np.sum(law[i] == "MISDEMEANOR") for i in idx), dtype=int)
    vio = np.fromiter((np.sum(law[i] == "VIOLATION") for i in idx), dtype=int)

    violent = np.fromiter((np.sum(grp[i] == "violent") for i in idx), dtype=int)
    prop = np.fromiter((np.sum(grp[i] == "property") for i in idx), dtype=int)
    other = np.fromiter((np.sum(grp[i] == "other") for i in idx), dtype=int)

    return pd.DataFrame(
        {
            "id": airbnb["id"].to_numpy(),
            f"crimes_total_{int(radius_m)}m": total,
            f"felonies_{int(radius_m)}m": fel,
            f"misdemeanors_{int(radius_m)}m": mis,
            f"violations_{int(radius_m)}m": vio,
            f"violent_{int(radius_m)}m": violent,
            f"property_{int(radius_m)}m": prop,
            f"other_{int(radius_m)}m": other,
        }
    )


def main() -> None:
    print(f"Reading: {AIRBNB_CLEAN.relative_to(ROOT_DIR)}")
    airbnb = pd.read_csv(AIRBNB_CLEAN)

    print(f"Reading: {NYPD_CLEAN.relative_to(ROOT_DIR)}")
    nypd = pd.read_csv(NYPD_CLEAN)

    # Normalizacja (bezpiecznie)
    nypd["law_category"] = nypd["law_category"].astype(str).str.upper().str.strip()
    nypd["offense_description"] = nypd["offense_description"].astype(str).str.upper().str.strip()

    # Dodaj grupy violent/property/other
    nypd = add_offense_group(nypd)

    # Liczymy dla 3 promieni (do porównania w raporcie)
    radii = [300.0, 400.0, 500.0]
    feats = [counts_for_radius(airbnb, nypd, r) for r in radii]

    # Merge cech do jednego DF
    merged = airbnb.copy()
    for f in feats:
        merged = merged.merge(f, on="id", how="left")

    out_path = DATA_DIR / "merged_features.csv"
    merged.to_csv(out_path, index=False)

    print(f"Saved: {out_path.relative_to(ROOT_DIR)}")
    print(f"Rows: {len(merged)}")
    print("Example columns added:", [c for c in merged.columns if c.endswith("m")][:10])


if __name__ == "__main__":
    main()
