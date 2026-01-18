from __future__ import annotations

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from config import DATA_DIR, PLOTS_DIR, ROOT_DIR

TOP_N = 250


def main() -> None:
    PLOTS_DIR.mkdir(exist_ok=True)
    out_dir = PLOTS_DIR / "6-network"
    out_dir.mkdir(exist_ok=True)

    H = nx.read_graphml(DATA_DIR / "hotspot_projection.graphml")
    cent = pd.read_csv(DATA_DIR / "hotspot_centrality.csv")
    comm = pd.read_csv(DATA_DIR / "hotspot_communities.csv")

    lcc_nodes = max(nx.connected_components(H), key=len)
    H_lcc = H.subgraph(lcc_nodes).copy()

    top_nodes = (
        cent[cent["hotspot"].isin(H_lcc.nodes())]
        .sort_values("pagerank", ascending=False)["hotspot"]
        .head(TOP_N)
        .tolist()
    )

    nodes_keep: set[str] = set(top_nodes)
    for n in top_nodes:
        nodes_keep.update(H_lcc.neighbors(n))

    S = H_lcc.subgraph(nodes_keep).copy()

    isolates = list(nx.isolates(S))
    if isolates:
        S.remove_nodes_from(isolates)

    pos = nx.spring_layout(S, seed=42, k=None)

    comm_map = dict(zip(comm["hotspot"], comm["community_id"]))
    node_colors = [comm_map.get(n, -1) for n in S.nodes()]

    pr_map = dict(zip(cent["hotspot"], cent["pagerank"]))
    sizes = [20000 * pr_map.get(n, 0.0) + 20 for n in S.nodes()]

    plt.figure(figsize=(12, 10))
    nx.draw_networkx_edges(S, pos, alpha=0.25, width=0.8)
    nx.draw_networkx_nodes(S, pos, node_size=sizes, node_color=node_colors, cmap="tab20")
    plt.title(f"Hotspot projection (LCC) - top {TOP_N} nodes by PageRank (colored by community)")
    plt.axis("off")
    out1 = out_dir / f"hotspot_projection_top{TOP_N}.png"
    plt.tight_layout()
    plt.savefig(out1, dpi=200)
    plt.close()
    print(f"Saved: {out1.relative_to(ROOT_DIR)}")

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
