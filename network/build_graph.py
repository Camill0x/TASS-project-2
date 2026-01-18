from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

from config import DATA_DIR, DEFAULT_RADIUS_M, ROOT_DIR

RADIUS_M = float(DEFAULT_RADIUS_M)

EARTH_RADIUS_M = 6371000.0


def to_rad(df):
    return np.deg2rad(df[["latitude", "longitude"]].to_numpy())


def main() -> None:
    airbnb = pd.read_csv(DATA_DIR / f"merged_model_{DEFAULT_RADIUS_M}m.csv")
    hotspots = pd.read_csv(DATA_DIR / "hotspots.csv")

    print(f"Listings: {len(airbnb)} | Hotspots: {len(hotspots)}")

    hotspot_rad = np.deg2rad(hotspots[["lat_cell", "lon_cell"]].to_numpy())
    tree = BallTree(hotspot_rad, metric="haversine")
    radius_rad = RADIUS_M / EARTH_RADIUS_M

    listing_rad = to_rad(airbnb)
    neighbors = tree.query_radius(listing_rad, r=radius_rad)

    G = nx.Graph()

    for _, r in airbnb.iterrows():
        G.add_node(f"L_{r['id']}", node_type="listing", price=r["price"])

    for _, r in hotspots.iterrows():
        G.add_node(
            f"H_{r['hotspot_id']}",
            node_type="hotspot",
            violent=r["violent_crimes"],
            felony=r["felony_crimes"],
        )

    for i, hs_idx in enumerate(neighbors):
        listing_id = f"L_{airbnb.iloc[i]['id']}"
        for h in hs_idx:
            hotspot_id = f"H_{hotspots.iloc[h]['hotspot_id']}"
            weight = hotspots.iloc[h]["violent_crimes"]
            if weight > 0:
                G.add_edge(listing_id, hotspot_id, weight=weight)

    out = DATA_DIR / "bipartite_airbnb_hotspot.graphml"
    nx.write_graphml(G, out)
    print(f"Saved graph: {out.relative_to(ROOT_DIR)}")
    print(f"Nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")


if __name__ == "__main__":
    main()
