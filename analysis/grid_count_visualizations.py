from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import DATA_DIR, DEFAULT_RADIUS_M, PLOTS_DIR, ROOT_DIR


def save_hexbin_loglog(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    filename: str,
    gridsize: int = 55,
) -> None:
    """Hexbin density plot on log-log scale."""
    d = df[[x, y]].dropna()

    xs = np.log1p(d[x].to_numpy(dtype=float))
    ys = np.log1p(d[y].to_numpy(dtype=float))

    plt.figure(figsize=(7, 5))
    hb = plt.hexbin(xs, ys, gridsize=gridsize, bins="log")
    plt.xlabel(f"log({x})")
    plt.ylabel(f"log({y})")
    plt.title(title)
    plt.colorbar(hb, label="log(cell count)")

    out = PLOTS_DIR / "5-statistical" / filename
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out.relative_to(ROOT_DIR)}")


def bin_airbnb_counts(df: pd.DataFrame, airbnb_col: str) -> pd.Series:
    """Create bins for Airbnb counts"""
    x = df[airbnb_col].fillna(0).astype(int)

    bins = pd.cut(
        x,
        bins=[-1, 0, 10, 100, int(x.max())],
        labels=["0", "1-10", "11-100", "100+"],
        include_lowest=True,
    )
    return bins


def save_boxplot_by_bins(
    df: pd.DataFrame,
    airbnb_col: str,
    target_col: str,
    title: str,
    filename: str,
) -> None:
    """Boxplot of target_col grouped by Airbnb count bins."""
    bins = bin_airbnb_counts(df, airbnb_col)
    order = ["0", "1-10", "11-100", "100+"]

    plt.figure(figsize=(8, 5))
    data = []
    for b in order:
        vals = df.loc[bins == b, target_col].dropna().to_numpy(dtype=float)
        data.append(vals)

    plt.boxplot(data, tick_labels=order, showfliers=False)
    plt.xlabel(f"{airbnb_col} bin")
    plt.ylabel(target_col)
    plt.title(title)

    out = PLOTS_DIR / "5-statistical" / filename
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out.relative_to(ROOT_DIR)}")


def main() -> None:
    PLOTS_DIR.mkdir(exist_ok=True)

    R = int(DEFAULT_RADIUS_M)
    path = DATA_DIR / f"grid_counts_{R}m.csv"
    print(f"Reading: {path.relative_to(ROOT_DIR)}")

    df = pd.read_csv(path)

    required = ["airbnb_count", "nypd_count"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # --- hexbin: Airbnb vs NYPD (log–log density) ---
    save_hexbin_loglog(
        df,
        "airbnb_count",
        "nypd_count",
        f"Airbnb vs NYPD — hexbin",
        f"hexbin_airbnb_vs_nypd_{R}m.png",
        gridsize=55,
    )

    # --- boxplot: NYPD counts by Airbnb density bins ---
    save_boxplot_by_bins(
        df,
        "airbnb_count",
        "nypd_count",
        f"NYPD distribution by Airbnb bins",
        f"boxplot_nypd_by_airbnb_bins_{R}m.png",
    )


if __name__ == "__main__":
    main()
