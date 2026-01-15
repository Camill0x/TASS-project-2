from __future__ import annotations

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from config import DATA_DIR, PLOTS_DIR, ROOT_DIR

TOP_N = 250  # sensowny rozmiar do rysowania


def main() -> None:
    PLOTS_DIR.mkdir(exist_ok=True)
    out_dir = PLOTS_DIR / "6-network"
    out_dir.mkdir(exist_ok=True)

    H = nx.read_graphml(DATA_DIR / "hotspot_projection.graphml")
    cent = pd.read_csv(DATA_DIR / "hotspot_centrality.csv")
    comm = pd.read_csv(DATA_DIR / "hotspot_communities.csv")

    # Weź TOP_N hotspotów wg PageRank
    top_nodes = cent.sort_values("pagerank", ascending=False)["hotspot"].head(TOP_N).tolist()
    S = H.subgraph(top_nodes).copy()

    # Layout
    pos = nx.spring_layout(S, seed=42, k=None)

    # Community colors (proste mapowanie na liczby)
    comm_map = dict(zip(comm["hotspot"], comm["community_id"]))
    node_colors = [comm_map.get(n, -1) for n in S.nodes()]

    # Node sizes wg PageRank
    pr_map = dict(zip(cent["hotspot"], cent["pagerank"]))
    sizes = [20000 * pr_map.get(n, 0.0) + 20 for n in S.nodes()]

    plt.figure(figsize=(12, 10))
    nx.draw_networkx_edges(S, pos, alpha=0.25, width=0.8)
    nx.draw_networkx_nodes(S, pos, node_size=sizes, node_color=node_colors)
    plt.title(f"Hotspot projection – top {TOP_N} nodes by PageRank (colored by community)")
    plt.axis("off")
    out1 = out_dir / f"hotspot_projection_top{TOP_N}.png"
    plt.tight_layout()
    plt.savefig(out1, dpi=200)
    plt.close()
    print(f"Saved: {out1.relative_to(ROOT_DIR)}")

    # Druga wizualizacja: histogram wielkości community (na LCC)
    # (dla raportu: pokazuje strukturę społeczności)
    comm_valid = comm[comm["community_id"] >= 0]
    counts = comm_valid["community_id"].value_counts().sort_values(ascending=False)

    plt.figure(figsize=(9, 4))
    plt.bar(counts.index.astype(str), counts.values)
    plt.title("Community sizes (number of hotspots per community)")
    plt.xlabel("community_id")
    plt.ylabel("hotspots count")
    plt.xticks(rotation=90)
    plt.tight_layout()
    out2 = out_dir / "community_sizes.png"
    plt.savefig(out2, dpi=200)
    plt.close()
    print(f"Saved: {out2.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
