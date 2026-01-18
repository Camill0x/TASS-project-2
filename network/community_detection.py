from __future__ import annotations

import networkx as nx
import pandas as pd
from networkx.algorithms.community import greedy_modularity_communities, modularity

from config import DATA_DIR, ROOT_DIR


def main() -> None:
    proj_path = DATA_DIR / "hotspot_projection.graphml"
    print(f"Reading projection graph: {proj_path.relative_to(ROOT_DIR)}")
    H = nx.read_graphml(proj_path)

    # LCC ( Largest Connected Component )
    components = list(nx.connected_components(H))
    largest_cc = max(components, key=len) if components else set()
    H_lcc = H.subgraph(largest_cc).copy()

    print(f"LCC: {H_lcc.number_of_nodes()} nodes, {H_lcc.number_of_edges()} edges")

    # Community detection (greedy modularity)
    comms = list(greedy_modularity_communities(H_lcc, weight="weight"))
    print(f"Detected communities: {len(comms)}")

    # Modularity score
    mod = modularity(H_lcc, comms, weight="weight")
    print(f"Modularity (LCC): {mod:.4f}")

    # community assignment
    mapping = {}
    for i, c in enumerate(comms):
        for node in c:
            mapping[node] = i

    df = pd.DataFrame([{"hotspot": n, "community_id": mapping.get(n, -1)} for n in H.nodes()])

    out = DATA_DIR / "hotspot_communities.csv"
    df.to_csv(out, index=False)
    print(f"Saved: {out.relative_to(ROOT_DIR)}")

    out2 = DATA_DIR / "community_stats.csv"
    pd.DataFrame(
        {
            "communities": [len(comms)],
            "modularity_lcc": [mod],
            "lcc_nodes": [H_lcc.number_of_nodes()],
            "lcc_edges": [H_lcc.number_of_edges()],
        }
    ).to_csv(out2, index=False)
    print(f"Saved: {out2.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
