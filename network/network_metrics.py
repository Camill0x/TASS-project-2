from __future__ import annotations

import networkx as nx
import pandas as pd

from config import DATA_DIR, ROOT_DIR


def main() -> None:
    path = DATA_DIR / "bipartite_airbnb_hotspot.graphml"
    print(f"Reading graph: {path.relative_to(ROOT_DIR)}")
    G = nx.read_graphml(path)

    listings = [n for n, d in G.nodes(data=True) if d.get("node_type") == "listing"]
    hotspots = [n for n, d in G.nodes(data=True) if d.get("node_type") == "hotspot"]

    print(f"Listings: {len(listings)}, Hotspots: {len(hotspots)}")

    # Projection onto hotspots
    H = nx.bipartite.weighted_projected_graph(G, hotspots)
    print(f"Hotspot projection: {H.number_of_nodes()} nodes, {H.number_of_edges()} edges")

    proj_path = DATA_DIR / "hotspot_projection.graphml"
    nx.write_graphml(H, proj_path)
    print(f"Saved projection graph: {proj_path.relative_to(ROOT_DIR)}")

    # Global metrics
    components = list(nx.connected_components(H))
    n_components = len(components)
    largest_cc = max(components, key=len) if components else set()
    H_lcc = H.subgraph(largest_cc).copy()

    global_stats = {
        "nodes": H.number_of_nodes(),
        "edges": H.number_of_edges(),
        "connected_components": n_components,
        "largest_component_nodes": H_lcc.number_of_nodes(),
        "largest_component_edges": H_lcc.number_of_edges(),
        "density": nx.density(H) if H.number_of_nodes() > 1 else 0.0,
        "avg_clustering": nx.average_clustering(H_lcc) if H_lcc.number_of_nodes() > 2 else 0.0,
    }

    out_global = DATA_DIR / "network_global_stats.csv"
    pd.DataFrame([global_stats]).to_csv(out_global, index=False)
    print(f"Saved: {out_global.relative_to(ROOT_DIR)}")
    print(global_stats)

    # Centrality measures
    deg_cent = nx.degree_centrality(H)
    pr = nx.pagerank(H, weight="weight")

    # Weighted degree (strength)
    strength = dict(H.degree(weight="weight"))

    # Betweenness
    bet = nx.betweenness_centrality(H_lcc, normalized=True, weight=None)

    rows = []
    for n in H.nodes():
        rows.append(
            {
                "hotspot": n,
                "degree_centrality": deg_cent.get(n, 0.0),
                "pagerank": pr.get(n, 0.0),
                "strength_weighted_degree": float(strength.get(n, 0.0)),
                "betweenness_lcc": bet.get(n, 0.0) if n in H_lcc else 0.0,
            }
        )

    df = pd.DataFrame(rows).sort_values("pagerank", ascending=False)

    out = DATA_DIR / "hotspot_centrality.csv"
    df.to_csv(out, index=False)
    print(f"Saved: {out.relative_to(ROOT_DIR)}")

    print("\nTop 10 hotspots by PageRank:")
    print(df.head(10))


if __name__ == "__main__":
    main()
