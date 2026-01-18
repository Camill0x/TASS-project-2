import math
import folium
import pandas as pd

from config import DATA_DIR, DEFAULT_RADIUS_M, PLOTS_DIR


def radius_from_count(v: int) -> float:
    if v <= 0:
        return 0
    return 2.0 + 3.0 * math.log10(v + 1)


def add_layer(m: folium.Map, df: pd.DataFrame, col: str, name: str, color: str):
    fg = folium.FeatureGroup(name=name, show=False)
    for _, r in df.iterrows():
        v = int(r[col])
        if v <= 0:
            continue
        folium.CircleMarker(
            location=[r["cell_lat_center"], r["cell_lon_center"]],
            radius=radius_from_count(v),
            color=color,
            fill=True,
            fill_opacity=0.55,
            weight=0,
            popup=f"{col}={v}",
        ).add_to(fg)
    fg.add_to(m)


def main():
    outdir = PLOTS_DIR / "4-3-grid"
    outdir.mkdir(parents=True, exist_ok=True)

    path = DATA_DIR / f"grid_counts_{DEFAULT_RADIUS_M}m.csv"
    df = pd.read_csv(path)

    m = folium.Map(location=[40.73, -73.93], zoom_start=11, tiles="cartodbpositron")

    add_layer(m, df, "airbnb_count", "Grid: Airbnb count", "navy")
    add_layer(m, df, "nypd_count", "Grid: NYPD all", "red")
    add_layer(m, df, "felony", "Grid: Felony", "darkgreen")
    add_layer(m, df, "violent_count", "Grid: Violent", "purple")

    folium.LayerControl(collapsed=False).add_to(m)

    out = outdir / f"grid_layers_{DEFAULT_RADIUS_M}m.html"
    m.save(out)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
