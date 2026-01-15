from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import DATA_DIR, DEFAULT_RADIUS_M, PLOTS_DIR, ROOT_DIR


def add_crime_zone(df: pd.DataFrame, col: str, out_col: str) -> pd.DataFrame:
    """Create low/mid/high zones based on terciles of a crime measure."""
    df = df.copy()
    q1, q2 = df[col].quantile([0.33, 0.66]).tolist()

    def zone(x):
        if x <= q1:
            return "low"
        if x <= q2:
            return "mid"
        return "high"

    df[out_col] = df[col].apply(zone)
    return df


def save_boxplot(df: pd.DataFrame, y: str, zone_col: str, title: str, filename: str) -> None:
    plt.figure(figsize=(7, 5))
    order = ["low", "mid", "high"]
    data = [df.loc[df[zone_col] == z, y].dropna() for z in order]
    plt.boxplot(data, tick_labels=order, showfliers=False)
    plt.xlabel(f"Crime zone ({zone_col})")
    plt.ylabel(y)
    plt.title(title)
    out = PLOTS_DIR / "5-statistical" / filename
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out.relative_to(ROOT_DIR)}")


def save_hexbin(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    filename: str,
    gridsize: int = 55,
) -> None:
    """Hexbin density plot on log-log scale."""
    d = df[[x, y]].dropna()

    hb = plt.hexbin(d[x], d[y], gridsize=gridsize, bins="log")
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(title)
    plt.colorbar(hb, label="log(cell count)")

    out = PLOTS_DIR / "5-statistical" / filename
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out.relative_to(ROOT_DIR)}")


def corr_table(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    return df[cols].corr(numeric_only=True)


def save_corr_heatmap(corr: pd.DataFrame, title: str, filename: str) -> None:
    plt.figure(figsize=(10, 8))
    plt.imshow(corr.values)
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.index)), corr.index)
    plt.title(title)
    plt.colorbar()
    plt.tight_layout()
    out = PLOTS_DIR / "5-statistical" / filename
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out.relative_to(ROOT_DIR)}")


def zone_summary(
    df: pd.DataFrame,
    zone_col: str,
    violent_col: str,
    fel_col: str,
    tot_col: str,
) -> pd.DataFrame:
    """Aggregate key stats by zone."""
    zs = (
        df.groupby(zone_col)
        .agg(
            n=("id", "count"),
            price_mean=("price", "mean"),
            price_median=("price", "median"),
            log_price_mean=("log_price", "mean"),
            violent_mean=(violent_col, "mean"),
            felonies_mean=(fel_col, "mean"),
            total_mean=(tot_col, "mean"),
        )
        .reset_index()
        .rename(columns={zone_col: "crime_zone"})
    )

    order = pd.Categorical(zs["crime_zone"], categories=["low", "mid", "high"], ordered=True)
    zs = zs.assign(_order=order).sort_values("_order").drop(columns="_order")
    return zs


def zone_room_summary(df: pd.DataFrame, zone_col: str, name: str, R: int) -> None:
    """Save price/review/availability summary by (crime_zone x room_type)."""
    if "room_type" not in df.columns:
        return

    tab = (
        df.groupby([zone_col, "room_type"])
        .agg(
            n=("id", "count"),
            price_mean=("price", "mean"),
            price_median=("price", "median"),
            log_price_mean=("log_price", "mean"),
            reviews_mean=("number_of_reviews", "mean"),
            reviews_pm_mean=("reviews_per_month", "mean"),
            avail_mean=("availability_365", "mean"),
        )
        .reset_index()
        .rename(columns={zone_col: "crime_zone"})
    )

    outp = DATA_DIR / f"zone_roomtype_summary_{name}_{R}m.csv"
    tab.to_csv(outp, index=False)
    print(f"Saved: {outp.relative_to(ROOT_DIR)}")


def plot_mean_by_zone_and_room(df: pd.DataFrame, zone_col: str, y: str, title: str, filename: str) -> None:
    """Line chart: mean(y) across zones for each room_type."""
    if "room_type" not in df.columns:
        return
    order = ["low", "mid", "high"]
    pivot = (
        df.groupby([zone_col, "room_type"])[y]
        .mean()
        .reset_index()
        .pivot(index=zone_col, columns="room_type", values=y)
        .reindex(order)
    )
    plt.figure(figsize=(8, 5))
    for col in pivot.columns:
        plt.plot(pivot.index, pivot[col], marker="o", label=col)
    plt.title(title)
    plt.xlabel(zone_col)
    plt.ylabel(y)
    plt.legend()
    plt.tight_layout()
    out = PLOTS_DIR / "5-statistical" / filename
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out.relative_to(ROOT_DIR)}")


def main() -> None:
    PLOTS_DIR.mkdir(exist_ok=True)

    path = DATA_DIR / "merged_features.csv"
    print(f"Reading: {path.relative_to(ROOT_DIR)}")
    df = pd.read_csv(path)

    # --- modelling convenience / "standard mieszkania" ---
    df["reviews_per_month"] = df["reviews_per_month"].fillna(0)
    df = df[df["price"].notna()]
    df = df[df["price"] >= 10]  # drop degenerate
    df = df[df["price"] <= 1000]  # cut outliers for stats/models
    df["log_price"] = np.log1p(df["price"])

    # --- radius-dependent columns ---
    R = int(DEFAULT_RADIUS_M)
    violent_col = f"violent_{R}m"
    fel_col = f"felonies_{R}m"
    tot_col = f"crimes_total_{R}m"

    required = [violent_col, fel_col, tot_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}. Did you generate merged_features.csv with this radius?")

    # --- zones (two definitions) ---
    df = add_crime_zone(df, violent_col, "crime_zone_violent")
    df = add_crime_zone(df, fel_col, "crime_zone_felony")

    # --- save zone summaries (two CSVs) ---
    zs_v = zone_summary(df, "crime_zone_violent", violent_col, fel_col, tot_col)
    zs_f = zone_summary(df, "crime_zone_felony", violent_col, fel_col, tot_col)

    out_v = DATA_DIR / "crime_zone_summary_violent.csv"
    out_f = DATA_DIR / "crime_zone_summary_felony.csv"
    zs_v.to_csv(out_v, index=False)
    zs_f.to_csv(out_f, index=False)

    print(f"Saved: {out_v.relative_to(ROOT_DIR)}")
    print(zs_v)
    print(f"Saved: {out_f.relative_to(ROOT_DIR)}")
    print(zs_f)

    # --- boxplots (violent zones) ---
    save_boxplot(
        df, "price", "crime_zone_violent", f"Price by violent-crime zone (R={R}m)", "boxplot_price_by_zone_violent.png"
    )
    save_boxplot(
        df,
        "log_price",
        "crime_zone_violent",
        f"Log(price) by violent-crime zone (R={R}m)",
        "boxplot_logprice_by_zone_violent.png",
    )

    # --- boxplots (felony zones) ---
    save_boxplot(
        df, "price", "crime_zone_felony", f"Price by felony-crime zone (R={R}m)", "boxplot_price_by_zone_felony.png"
    )
    save_boxplot(
        df,
        "log_price",
        "crime_zone_felony",
        f"Log(price) by felony-crime zone (R={R}m)",
        "boxplot_logprice_by_zone_felony.png",
    )

    # --- hexbin: price/log_price vs crimes ---
    save_hexbin(df, tot_col, "log_price", f"log_price vs {tot_col}", f"hexbin_logprice_vs_{tot_col}.png")
    save_hexbin(df, violent_col, "log_price", f"log_price vs {violent_col}", f"hexbin_logprice_vs_{violent_col}.png")
    save_hexbin(df, fel_col, "log_price", f"log_price vs {fel_col}", f"hexbin_logprice_vs_{fel_col}.png")

    # --- correlations table ---
    corr_cols = [
        "price",
        "log_price",
        "number_of_reviews",
        "reviews_per_month",
        "availability_365",
        tot_col,
        fel_col,
        violent_col,
        f"misdemeanors_{R}m",
        f"violations_{R}m",
        f"property_{R}m",
        f"other_{R}m",
    ]
    corr_cols = [c for c in corr_cols if c in df.columns]
    corr = corr_table(df, corr_cols)

    corr_out = DATA_DIR / "correlations.csv"
    corr.to_csv(corr_out)
    print(f"Saved: {corr_out.relative_to(ROOT_DIR)}")

    # Correlation heatmap to PNG (raport-friendly)
    save_corr_heatmap(corr, f"Correlation heatmap (R={R}m)", f"corr_heatmap_{R}m.png")

    # --- correlations by room_type (standard mieszkania) ---
    if "room_type" in df.columns:
        room_corrs = []
        for rt, sub in df.groupby("room_type"):
            c = sub[corr_cols].corr(numeric_only=True)
            row = c.loc["log_price"].to_frame().T
            row.insert(0, "room_type", rt)
            room_corrs.append(row)
        room_corr = pd.concat(room_corrs, ignore_index=True)
        out_room = DATA_DIR / f"correlations_by_room_type_{R}m.csv"
        room_corr.to_csv(out_room, index=False)
        print(f"Saved: {out_room.relative_to(ROOT_DIR)}")

    # --- zone x room_type summaries (two defs) ---
    zone_room_summary(df, "crime_zone_violent", "violent", R)
    zone_room_summary(df, "crime_zone_felony", "felony", R)

    # --- optional: mean log_price by zone & room_type (nice single chart for report) ---
    plot_mean_by_zone_and_room(
        df,
        "crime_zone_violent",
        "log_price",
        f"Mean log_price by violent zone & room_type (R={R}m)",
        f"mean_logprice_by_zone_roomtype_violent_{R}m.png",
    )
    plot_mean_by_zone_and_room(
        df,
        "crime_zone_felony",
        "log_price",
        f"Mean log_price by felony zone & room_type (R={R}m)",
        f"mean_logprice_by_zone_roomtype_felony_{R}m.png",
    )

    # --- store modelling dataset used later (regression, network linkage) ---
    model_out = DATA_DIR / f"merged_model_{R}m.csv"
    df.to_csv(model_out, index=False)
    print(f"Saved: {model_out.relative_to(ROOT_DIR)}")
    print(f"Rows in modelling dataset: {len(df)}")


if __name__ == "__main__":
    main()
