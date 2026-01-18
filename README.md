# TASS Project 2 - Airbnb & NYPD Analysis

A Python project for collecting, cleaning, and analyzing NYC Airbnb listings together with NYPD complaint records (2018-2019).
The goal is to build a unified dataset suitable for spatial analysis and further exploration.

## Environment setup

1. **Create and activate a Conda environment:**

   ```sh
   conda create -n tass python=3.12
   conda activate tass
   ```

2. **Install required dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Export the project root to `PYTHONPATH`:**

   From the root directory of the project:

   ```sh
   export PYTHONPATH=$(pwd)
   ```

## Download raw datasets

Airbnb (2019 snapshot) and NYPD historic complaint data (2006–2019) are downloaded directly from Kaggle using `kagglehub`.

To download both datasets, run:

```sh
python3 utils/download_datasets.py
```

Downloaded files will be placed in the `data/` directory.

## Clean datasets

To clean and filter the raw datasets including coordinate filtering and restricting Airbnb and NYPD data to 2018–2019, run:

```sh
python3 utils/clean_datasets.py
```

The cleaned versions will be saved as:

- `data/airbnb_clean.csv`
- `data/nypd_clean.csv`

## Prepare Airbnb data for modeling

Filters Airbnb prices (10–1000 USD) and creates log-transformed prices:

```sh
python3 features/make_model_ready.py
```

Generated file:

- `data/airbnb_model.csv`

## Crime categories

Basic exploratory analysis of NYPD complaint categories.
The script identifies the most frequent offense types and saves them for reference:

```sh
python3 eda/eda_nypd_basic.py
```

Generated file:

- `plots/top30_offense_description.csv`

Crime categories are mapped into three groups:

- `violent`
- `property`
- `other`

The taxonomy definition is stored in:

- `features/crime_taxonomy.py`

## Spatial feature engineering

### Crime aggregation around Airbnb listings (radius-based)

Aggregates NYPD complaints within multiple distance buffers
around each Airbnb listing:

```sh
python3 features/build_features_radius.py
```

Generated file:

- `data/merged_features.csv`

Features include crime counts within 300 m, 400 m, and 500 m radii.

### Grid-based spatial aggregation

Aggregates Airbnb listings and NYPD complaints into a regular spatial grid:

```sh
python3 features/build_features_grid_counts.py
```

Generated file:

- `data/grid_counts_400m.csv`

Each grid cell contains counts of Airbnb listings and crime categories.

## Spatial exploratory analysis

### Interactive maps (Folium)

Generates interactive maps for Airbnb listings and crime categories:

```sh
python3 eda/eda_folium_maps.py:
```

Generated files:

- `plots/4-1-folium/map_airbnb.html`
- `plots/4-1-folium/map_crimes_all.html`
- `plots/4-1-folium/map_crimes_felony.html`
- `plots/4-1-folium/map_crimes_violent.html`

To generate a combined interactive map with layer controls, run:

```sh
python3 eda/eda_all_layers_map.py
```

Generated file:

- `plots/4-1-folium/map_layers_airbnb_crime.html`

### Density maps (hexbin)

Static hexbin density maps for Airbnb listings and crime categories:

```sh
python3 eda/eda_hexbin_maps.py
```

Generated files:

- `plots/4-2-hexbin/felony_hexbin.png`
- `plots/4-2-hexbin/violent_hexbin.png`
- `plots/4-2-hexbin/nypd_all_hexbin.png`
- `plots/4-2-hexbin/airbnb_hexbin.png`

### Grid maps

Static grid density maps for Airbnb listings and crime categories:

```sh
python3 eda/eda_grid_maps.py
```

Generated files:

- `grid_layers_400m.html`

## Statistical analysis

The default analysis radius is defined in `config.py`
(e.g. `DEFAULT_RADIUS_M = 400`).

```sh
python3 analysis/statistical_analysis.py
```

Airbnb listings are divided into terciles based on crime intensity:

- `crime_zone_violent`
- `crime_zone_felony`

Generated summary tables:

- `data/crime_zone_summary_violent.csv`
- `data/crime_zone_summary_felony.csv`

Additional outputs include:

- correlation heatmaps
- boxplots of price and log-price by crime zone
- room-type–specific summaries
- final modeling dataset

### Borough-level aggregation

Aggregates Airbnb listings and NYPD complaints at the borough level
and joins them by borough name:

```sh
python3 analysis/borough_join.py
```

Generated files:

- `data/borough_join_summary.csv`
- `plots/5-statistical/borough_airbnb_listings.png`
- `plots/5-statistical/borough_crimes_total.png`

### Grid-based statistical visualizations

Explores relationships between Airbnb density and crime density
using grid-aggregated data:

```sh
python3 analysis/grid_count_visualizations.py
```

Generated plots:

- `hexbin_airbnb_vs_nypd_loglog_{R}m.png`
- `boxplot_nypd_by_airbnb_bins_{R}m.png`

### Regression models

Runs two regression models:

- baseline model
- extended model

Run:

```sh
python3 analysis/regression_models.py
```

Generated file:

- `data/regression_results.csv`

## Network analysis (SNA)

### Crime hotspots (grid-based)

Detects crime hotspots based on spatial grid aggregation:

```sh
python3 network/build_hotspots.py
```

Generated file:

- `data/hotspots.csv`

### Bipartite Airbnb–hotspot graph

Builds a bipartite network connecting Airbnb listings to nearby hotspots:

```sh
python3 network/build_graph.py
```

Generated file:

- `data/bipartite_airbnb_hotspot.graphml`

### Network metrics

Computes centrality measures and global network statistics
for the hotspot projection:

```sh
python3 network/network_metrics.py
```

Generated files:

- `data/hotspot_centrality.csv`
- `data/network_global_stats.csv`

### Community detection

Performs community detection on the hotspot projection network:

```sh
python3 network/community_detection.py
```

Generated files:

- `data/hotspot_projection.graphml`
- `data/hotspot_communities.csv`
- `data/community_stats.csv`

### Network visualizations

Generates static and interactive network visualizations:

```sh
python3 network/visualize_graph.py
python3 network/community_map.py
```

Generated files:

- `plots/6-network/hotspot_projection_top250.png`
- `plots/6-network/community_sizes.png`
- `plots/6-network/community_map.html`
