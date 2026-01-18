from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from config import DATA_DIR, PLOTS_DIR, RADII_M, ROOT_DIR


@dataclass(frozen=True)
class RunOutputs:
    """Files produced by the network pipeline (relative to project root)."""

    # data/
    hotspots_csv: Path = DATA_DIR / "hotspots.csv"
    bipartite_graph: Path = DATA_DIR / "bipartite_airbnb_hotspot.graphml"
    hotspot_projection: Path = DATA_DIR / "hotspot_projection.graphml"
    hotspot_centrality: Path = DATA_DIR / "hotspot_centrality.csv"
    hotspot_communities: Path = DATA_DIR / "hotspot_communities.csv"
    community_stats: Path = DATA_DIR / "community_stats.csv"
    global_stats: Path = DATA_DIR / "network_global_stats.csv"

    # plots/6-network/
    plot_projection_top250: Path = PLOTS_DIR / "6-network" / "hotspot_projection_top250.png"
    plot_community_sizes: Path = PLOTS_DIR / "6-network" / "community_sizes.png"
    map_community_html: Path = PLOTS_DIR / "6-network" / "community_map.html"


def run_module(module: str, env: dict[str, str]) -> None:
    """Run `python -m <module>` with given environment."""
    cmd = ["python", "-m", module]
    print(f"\n>>> Running: {' '.join(cmd)}  (RADIUS_M={env.get('RADIUS_M')})")
    subprocess.run(cmd, check=True, env=env, cwd=str(ROOT_DIR))


def copy_if_exists(src: Path, dst: Path) -> None:
    """Copy file if it exists, otherwise warn."""
    if not src.exists():
        print(f"Warning: missing output file: {src.relative_to(ROOT_DIR)}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"Saved: {dst.relative_to(ROOT_DIR)}")


def archive_outputs(radius_m: int, outputs: RunOutputs) -> tuple[Path, Path]:
    """
    Copy outputs from default locations into radius-specific folders:
      data/multiscale/<R>m/
      plots/6-network/multiscale/<R>m/
    Returns: (data_dir, plots_dir)
    """
    data_out_dir = DATA_DIR / "multiscale" / f"{radius_m}m"
    plots_out_dir = PLOTS_DIR / "6-network" / "multiscale" / f"{radius_m}m"

    print(f"\nArchiving outputs for R={radius_m}m")
    print(f"Data:  {data_out_dir.relative_to(ROOT_DIR)}")
    print(f"Plots: {plots_out_dir.relative_to(ROOT_DIR)}")

    # data files
    copy_if_exists(outputs.hotspots_csv, data_out_dir / outputs.hotspots_csv.name)
    copy_if_exists(outputs.bipartite_graph, data_out_dir / outputs.bipartite_graph.name)
    copy_if_exists(outputs.hotspot_projection, data_out_dir / outputs.hotspot_projection.name)
    copy_if_exists(outputs.hotspot_centrality, data_out_dir / outputs.hotspot_centrality.name)
    copy_if_exists(outputs.hotspot_communities, data_out_dir / outputs.hotspot_communities.name)
    copy_if_exists(outputs.community_stats, data_out_dir / outputs.community_stats.name)
    copy_if_exists(outputs.global_stats, data_out_dir / outputs.global_stats.name)

    # plots
    copy_if_exists(outputs.plot_projection_top250, plots_out_dir / outputs.plot_projection_top250.name)
    copy_if_exists(outputs.plot_community_sizes, plots_out_dir / outputs.plot_community_sizes.name)
    copy_if_exists(outputs.map_community_html, plots_out_dir / outputs.map_community_html.name)

    return data_out_dir, plots_out_dir


def read_global_stats(path: Path) -> dict[str, float]:
    """Read global stats CSV saved by network_metrics/community_detection."""
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    # allow either "key,value" or 1-row table; handle both
    if set(df.columns) >= {"key", "value"}:
        return dict(zip(df["key"], df["value"]))
    if len(df) == 1:
        return df.iloc[0].to_dict()
    # fallback: try first two columns
    if df.shape[1] >= 2:
        return dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
    return {}


def top_hotspots(path: Path, k: int = 10) -> list[str]:
    """Return top-k hotspot ids by PageRank from hotspot_centrality.csv."""
    if not path.exists():
        return []
    df = pd.read_csv(path)
    required = {"hotspot", "pagerank"}
    if not required.issubset(df.columns):
        return []
    top = df.sort_values("pagerank", ascending=False).head(k)["hotspot"].astype(str).tolist()
    return top


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def summarize_runs(results: list[dict]) -> None:
    """Save multiscale summary CSVs."""
    if not results:
        return

    out_dir = DATA_DIR / "multiscale"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Global stats table
    rows = []
    for r in results:
        row = {"radius_m": r["radius_m"]}
        row.update(r.get("global_stats", {}))
        row["lcc_top10_hotspots"] = ";".join(r.get("top_hotspots", []))
        rows.append(row)

    stats_df = pd.DataFrame(rows).sort_values("radius_m")
    out_stats = out_dir / "multiscale_global_stats.csv"
    stats_df.to_csv(out_stats, index=False)
    print(f"\nSaved: {out_stats.relative_to(ROOT_DIR)}")

    # Jaccard overlaps for top hotspots
    overlaps = []
    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            r1 = results[i]["radius_m"]
            r2 = results[j]["radius_m"]
            s1 = set(results[i].get("top_hotspots", []))
            s2 = set(results[j].get("top_hotspots", []))
            overlaps.append(
                {
                    "radius_a": r1,
                    "radius_b": r2,
                    "top10_jaccard": jaccard(s1, s2),
                    "top10_intersection": len(s1 & s2),
                }
            )

    ov_df = pd.DataFrame(overlaps).sort_values(["radius_a", "radius_b"])
    out_ov = out_dir / "multiscale_top_hotspots_overlap.csv"
    ov_df.to_csv(out_ov, index=False)
    print(f"Saved: {out_ov.relative_to(ROOT_DIR)}")

    print("\n=== MULTISCALE SUMMARY (quick view) ===")
    cols_preview = [
        c
        for c in [
            "radius_m",
            "nodes",
            "edges",
            "density",
            "connected_components",
            "largest_component_nodes",
            "avg_clustering",
        ]
        if c in stats_df.columns
    ]
    if cols_preview:
        print(stats_df[cols_preview].to_string(index=False))
    if not ov_df.empty:
        print("\nTop-10 hotspot overlaps (Jaccard):")
        print(ov_df.to_string(index=False))


def main() -> None:
    # choose radii (meters) you want to compare
    radii = RADII_M

    # ensure base dirs exist
    (DATA_DIR / "multiscale").mkdir(parents=True, exist_ok=True)
    (PLOTS_DIR / "6-network" / "multiscale").mkdir(parents=True, exist_ok=True)

    outputs = RunOutputs()
    results: list[dict] = []

    base_env = os.environ.copy()

    print("=== STARTING PIPELINE ===")
    for r in radii:
        env = base_env.copy()
        env["RADIUS_M"] = str(r)

        # Run pipeline
        run_module(
            "analysis.statistical_analysis", env
        )  # since "build_graph.py" needs "merged_model_{RADIUS}m.csv" file
        run_module("network.build_hotspots", env)
        run_module("network.build_graph", env)
        run_module("network.network_metrics", env)
        run_module("network.community_detection", env)

        # Visuals
        # run_module("network.visualize_graph", env)
        # run_module("network.community_map", env)

        # Archive outputs into radius-specific folders
        data_dir, _plots_dir = archive_outputs(r, outputs)

        # Collect summary info for this radius
        gs = read_global_stats(data_dir / outputs.global_stats.name)
        top10 = top_hotspots(data_dir / outputs.hotspot_centrality.name, k=10)

        results.append(
            {
                "radius_m": r,
                "global_stats": gs,
                "top_hotspots": top10,
            }
        )

    print("=== PIPELINE FINISHED ===")

    summarize_runs(results)


if __name__ == "__main__":
    main()
