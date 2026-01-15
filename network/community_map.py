from __future__ import annotations

import folium
import pandas as pd

from config import DATA_DIR, PLOTS_DIR, ROOT_DIR


def color_for_comm(comm_id: int) -> str:
    """Simple stable palette for Folium markers."""
    palette = [
        "red",
        "blue",
        "green",
        "purple",
        "orange",
        "darkred",
        "lightred",
        "beige",
        "darkblue",
        "darkgreen",
        "cadetblue",
        "darkpurple",
        "white",
        "pink",
        "lightblue",
        "lightgreen",
        "gray",
        "black",
        "lightgray",
    ]
    if comm_id < 0:
        return "gray"
    return palette[comm_id % len(palette)]


def main() -> None:
    PLOTS_DIR.mkdir(exist_ok=True)
    out_dir = PLOTS_DIR / "6-network"
    out_dir.mkdir(exist_ok=True)

    hotspots = pd.read_csv(DATA_DIR / "hotspots.csv")
    comm = pd.read_csv(DATA_DIR / "hotspot_communities.csv")

    # hotspots.csv has hotspot_id; graph/community uses node name "H_<hotspot_id>"
    if "hotspot_id" not in hotspots.columns:
        raise ValueError("Expected column 'hotspot_id' in hotspots.csv")

    hotspots["hotspot"] = "H_" + hotspots["hotspot_id"].astype(str)

    # Merge on the graph node id
    df = hotspots.merge(comm, on="hotspot", how="left")
    df["community_id"] = df["community_id"].fillna(-1).astype(int)

    # Center around NYC
    m = folium.Map(location=[40.73, -73.93], zoom_start=11, tiles="cartodbpositron")

    # Add layer per community (toggleable)
    for comm_id, sub in df.groupby("community_id"):
        name = f"Community {comm_id}" if comm_id >= 0 else "Not in LCC / unassigned"
        fg = folium.FeatureGroup(name=name, show=(comm_id == 0))

        for _, r in sub.iterrows():
            folium.CircleMarker(
                location=[r["lat_cell"], r["lon_cell"]],
                radius=3,
                color=color_for_comm(comm_id),
                fill=True,
                fill_opacity=0.7,
                popup=folium.Popup(
                    f"hotspot: {r['hotspot']}<br>"
                    f"community: {comm_id}<br>"
                    f"total: {int(r['total_crimes'])}<br>"
                    f"violent: {int(r['violent_crimes'])}<br>"
                    f"felony: {int(r['felony_crimes'])}",
                    max_width=300,
                ),
            ).add_to(fg)

        fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    button_html = """
    <button onclick="
        var b=document.querySelectorAll('.leaflet-control-layers-overlays input');
        var on=[...b].some(x=>!x.checked);
        b.forEach(x=>{ if(x.checked!==on) x.click(); });
    "
    style="
        position:fixed;bottom:30px;right:12px;z-index:9999;
        background:white;padding:8px 10px;border:1px solid #ccc;
        border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.15);
    ">
    Zaznacz / odznacz wszystkie
    </button>
    """

    m.get_root().html.add_child(folium.Element(button_html))

    legend_html = """
    <div style="
        position: fixed;
        bottom: 30px;
        left: 30px;
        width: 260px;
        z-index: 9999;
        background: white;
        padding: 12px 14px;
        border: 1px solid #ccc;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
        font-size: 13px;
        line-height: 1.4;
        ">
      <b>Community map</b><br><br>
      Hotspoty przestępczości (grid) pokolorowane wg <i>community_id</i>.<br>
      Community wykryte na projekcji grafu hotspotów (LCC).<br>
      Warstwy można włączać/wyłączać w panelu.
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    out = out_dir / "community_map.html"
    m.save(out)
    print(f"Saved: {out.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
