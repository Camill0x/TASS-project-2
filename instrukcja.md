# Instrukcja uruchomienia projektu – TASS Projekt 2

Instrukcja opisuje **kolejność uruchamiania skryptów** w celu pełnego odtworzenia analizy.
Zakładamy środowisko Python (conda/base) oraz uruchamianie poleceń z katalogu głównego repozytorium.

---

## 1. Pipeline danych

### Pobranie i czyszczenie danych

Aktualizuje pliki:

- `data/nypd_clean.csv` (bez NaT, lata 2018–2019)
- `data/airbnb_clean.csv`

```
python -m utils.download_dataset
python -m utils.clean_dataset
```

### Przygotowanie danych do analiz statystycznych

Tworzy plik:

- `data/airbnb_model.csv` (ceny 10–1000 USD + `log_price`)

```
python -m features.make_model_ready
```

---

## 2. Kategorie przestępstw

Wyświetla w konsoli top 30 kategorii przestępstw (`offense_description`)  
oraz zapisuje listę do pliku:

- `plots/top30_offense_description.csv`

```
python -m eda.eda_nypd_basic
```

Przykład:

```
python -m eda.eda_nypd_basic
=== Basic EDA - NYPD dataset ===
Reading: data\nypd_clean.csv

--- General info ---
Rows: 922882

Columns: complaint_id, complaint_date, offense_description, law_category, borough, latitude, longitude

--- Complaints per year ---
complaint_date
2018    472213
2019    450669
Name: count, dtype: int64

--- Complaints per borough ---
borough
BROOKLYN         268702
MANHATTAN        230467
BRONX            201339
QUEENS           182585
STATEN ISLAND     39789
Name: count, dtype: int64

--- Law category distribution ---
law_category
MISDEMEANOR    497438
FELONY         281779
VIOLATION      143665
Name: count, dtype: int64

--- Top 30 offense types ---
offense_description
PETIT LARCENY                     176067
HARRASSMENT 2                     142277
ASSAULT 3 & RELATED OFFENSES      106121
CRIMINAL MISCHIEF & RELATED OF     94567
GRAND LARCENY                      86546
FELONY ASSAULT                     40916
OFF. AGNST PUB ORD SENSBLTY &      40048
DANGEROUS DRUGS                    28658
MISCELLANEOUS PENAL LAW            27568
ROBBERY                            26296
BURGLARY                           22512
OFFENSES AGAINST PUBLIC ADMINI     15220
DANGEROUS WEAPONS                  14199
SEX CRIMES                         13507
VEHICLE AND TRAFFIC LAWS           13503
GRAND LARCENY OF MOTOR VEHICLE     10868
FORGERY                             9954
INTOXICATED & IMPAIRED DRIVING      9349
THEFT-FRAUD                         7638
CRIMINAL TRESPASS                   6320
FRAUDS                              4703
UNAUTHORIZED USE OF A VEHICLE       3250
POSSESSION OF STOLEN PROPERTY       3179
RAPE                                2989
OTHER OFFENSES RELATED TO THEF      2647
OFFENSES AGAINST THE PERSON         2434
OFFENSES INVOLVING FRAUD            2141
ADMINISTRATIVE CODE                 2122
ARSON                               1437
NYS LAWS-UNCLASSIFIED FELONY        1360
```

Mapowanie przestępstw do grup:

- `violent`
- `property`
- `other`

znajduje się w pliku i zostało zrobione na podstawie powyższej listy:

- `features/crime_taxonomy.py`

---

## 3. Łączenie przestrzenne danych

Tworzy główny zbiór cech przestrzennych:

- `data/merged_features.csv`

Zawiera m.in. liczbę przestępstw w promieniu 300 m, 400 m i 500 m.

```
python -m features.build_features_radius
```

(Czas wykonania: ok. 5 minut)

---

## 4. Analiza przestrzenna

### 4.1 Mapy interaktywne (Folium)

Osobne mapy:

- `plots/4-1-folium/map_airbnb.html`
- `plots/4-1-folium/map_crimes_all.html`
- `plots/4-1-folium/map_crimes_felony.html`
- `plots/4-1-folium/map_crimes_violent.html`

```
python -m eda.eda_maps_by_category
```

Przykład:

```
python -m eda.eda_maps_by_category
Saved map: plots/4-1-folium/map_airbnb.html
Saved map: plots/4-1-folium/map_crimes_all.html
Saved map: plots/4-1-folium/map_crimes_felony.html
Saved map: plots/4-1-folium/map_crimes_violent.html
```

Jedna mapa z przełączanymi warstwami i legendą:

- `plots/4-1-folium/map_layers_airbnb_crime.html`

```
python -m eda.eda_all_layers_map
```

Przykład:

```
python -m eda.eda_all_layers_map
Saved interactive layered map: plots/4-1-folium/map_layers_airbnb_crime.html
```

### 4.2 Mapy gęstości (Hexbin)

Statyczne wykresy:

- `plots/4-2-hexbin/felony_hexbin.png`
- `plots/4-2-hexbin/violent_hexbin.png`

```
python -m eda.eda_hexbin_by_category
```

---

## 5. Analiza statystyczna

Domyślny promień analizy jest ustawiony w config.py jako DEFAULT_RADIUS_M (np. 400 m).

```
python -m analysis.statistical_analysis
```

Skrypt tworzy podział ofert na strefy:

- `crime_zone_violent` (tercyle wg `violent_{DEFAULT_RADIUS_M}m`)
- `crime_zone_felony` (tercyle wg `felonies_{DEFAULT_RADIUS_M}m`)

Wyniki:

- `data/crime_zone_summary_violent.csv`
- `data/crime_zone_summary_felony.csv`

  oraz boxploty cen/log(cen) dla obu definicji stref.

Dodatkowe artefakty (korelacje + standard mieszkania):

- heatmapa korelacji: `plots/5-statistical/corr_heatmap_{R}m.png`
- korelacje `log_price` vs cechy per `room_type`: `data/correlations_by_room_type_{R}m.csv`
- podsumowania `crime_zone x room_type`: `data/zone_roomtype_summary_violent_{R}m.csv`, `data/zone_roomtype_summary_felony_{R}m.csv`

Przykład:

```
python -m analysis.statistical_analysis
Reading: data\merged_features.csv
Saved: data\crime_zone_summary_violent.csv
  crime_zone      n  price_mean  price_median  log_price_mean  violent_mean  felonies_mean   total_mean
1        low  16073  133.750016         100.0        4.675084    113.963915     256.188390   776.634480
2        mid  16052  142.194617         105.0        4.724014    287.839833     548.678171  1710.958136
0       high  16520  147.811138         112.0        4.770832    620.489104     920.003208  2908.490315
Saved: data\crime_zone_summary_felony.csv
  crime_zone      n  price_mean  price_median  log_price_mean  violent_mean  felonies_mean   total_mean
1        low  16055  122.668452          95.0        4.590029    128.086951     227.739209   719.033572
2        mid  16103  128.506676          99.0        4.643093    315.817053     514.108427  1629.896976
0       high  16487  171.973494         140.0        4.932735    579.886517     981.895433  3045.131983
Saved: plots\5-statistical\boxplot_price_by_zone_violent.png
Saved: plots\5-statistical\boxplot_logprice_by_zone_violent.png
Saved: plots\5-statistical\boxplot_price_by_zone_felony.png
Saved: plots\5-statistical\boxplot_logprice_by_zone_felony.png
Saved: plots\5-statistical\scatter_logprice_vs_violent_400m.png
Saved: plots\5-statistical\scatter_logprice_vs_felonies_400m.png
Saved: plots\5-statistical\scatter_logprice_vs_crimes_total_400m.png
Saved: plots\5-statistical\scatter_price_vs_violent_400m.png
Saved: data\correlations.csv
Saved: plots\5-statistical\corr_heatmap_400m.png
Saved: data\correlations_by_room_type_400m.csv
Saved: data\zone_roomtype_summary_violent_400m.csv
Saved: data\zone_roomtype_summary_felony_400m.csv
Saved: plots\5-statistical\mean_logprice_by_zone_roomtype_violent_400m.png
Saved: plots\5-statistical\mean_logprice_by_zone_roomtype_felony_400m.png
Saved: data\merged_model_400m.csv
Rows in modelling dataset: 48645
```

### 5A. Łączenie po dzielnicach (borough join)

Agregacja ofert Airbnb i przestępstw NYPD w skali dzielnic (borough) oraz złączenie tabel po nazwie dzielnicy.
Tworzy:

- `data/borough_join_summary.csv`
- `plots/5-statistical/borough_airbnb_listings.png`
- `plots/5-statistical/borough_crimes_total.png`

```
python -m analysis.borough_join
```

Przykład:

```
python -m analysis.borough_join
Reading: data\airbnb_clean.csv
Reading: data\nypd_clean.csv
Saved: data\borough_join_summary.csv
         borough  listings   avg_price  median_price  crimes_total  felonies  misdemeanors  violations  violent  property
2      Manhattan     21661  196.875814         150.0        230467     72050        128594       29823    40972     98619
1       Brooklyn     20104  124.383207          90.0        268702     87381        139528       41793    55962     85381
3         Queens      5666   99.517649          75.0        182585     57720         94791       30074    38952     59144
0          Bronx      1091   87.496792          65.0        201339     55202        112821       33316    51127     52147
4  Staten Island       373  114.812332          75.0         39789      9426         21704        8659     6687      9778
Saved: plots\5-statistical\borough_airbnb_listings.png
Saved: plots\5-statistical\borough_crimes_total.png
```

### Modele regresji

Uruchamia dwa modele:

- bazowy
- rozszerzony (uwagi prowadzącego)

Wyniki zapisywane do:

- `data/regression_results.csv`

```
python -m analysis.regression_models
```

Przykład:

```
python -m analysis.regression_models
Reading: data\merged_model_400m.csv

Running model: Model_A_basic
                            OLS Regression Results
==============================================================================
Dep. Variable:              log_price   R-squared:                       0.480
Model:                            OLS   Adj. R-squared:                  0.480
Method:                 Least Squares   F-statistic:                     6417.
Date:                Mon, 12 Jan 2026   Prob (F-statistic):               0.00
Time:                        12:24:43   Log-Likelihood:                -33038.
No. Observations:               48645   AIC:                         6.609e+04
Df Residuals:                   48637   BIC:                         6.616e+04
Df Model:                           7
Covariance Type:            nonrobust
=============================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
---------------------------------------------------------------------------------------------
Intercept                     4.7455      0.015    310.642      0.000       4.716       4.775
borough[T.Brooklyn]           0.2101      0.015     14.111      0.000       0.181       0.239
borough[T.Manhattan]          0.5007      0.015     33.132      0.000       0.471       0.530
borough[T.Queens]             0.1156      0.016      7.245      0.000       0.084       0.147
borough[T.Staten Island]      0.0300      0.029      1.040      0.298      -0.027       0.087
room_type[T.Private room]    -0.7648      0.004   -171.526      0.000      -0.774      -0.756
room_type[T.Shared room]     -1.1121      0.014    -77.322      0.000      -1.140      -1.084
crimes_total_400m          1.848e-05   2.57e-06      7.196      0.000    1.34e-05    2.35e-05
==============================================================================
Omnibus:                     5964.999   Durbin-Watson:                   1.876
Prob(Omnibus):                  0.000   Jarque-Bera (JB):            13275.858
Skew:                           0.744   Prob(JB):                         0.00
Kurtosis:                       5.082   Cond. No.                     3.52e+04
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 3.52e+04. This might indicate that there are
strong multicollinearity or other numerical problems.

Running model: Model_B_extended
                            OLS Regression Results
==============================================================================
Dep. Variable:              log_price   R-squared:                       0.510
Model:                            OLS   Adj. R-squared:                  0.510
Method:                 Least Squares   F-statistic:                     5069.
Date:                Mon, 12 Jan 2026   Prob (F-statistic):               0.00
Time:                        12:24:43   Log-Likelihood:                -31581.
No. Observations:               48645   AIC:                         6.318e+04
Df Residuals:                   48634   BIC:                         6.328e+04
Df Model:                          10
Covariance Type:            nonrobust
=============================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
---------------------------------------------------------------------------------------------
Intercept                     4.7236      0.015    312.981      0.000       4.694       4.753
borough[T.Brooklyn]           0.1610      0.015     10.997      0.000       0.132       0.190
borough[T.Manhattan]          0.4231      0.015     28.338      0.000       0.394       0.452
borough[T.Queens]             0.0587      0.016      3.771      0.000       0.028       0.089
borough[T.Staten Island]     -0.0500      0.028     -1.784      0.074      -0.105       0.005
room_type[T.Private room]    -0.7369      0.004   -168.346      0.000      -0.745      -0.728
room_type[T.Shared room]     -1.1152      0.014    -79.621      0.000      -1.143      -1.088
felonies_400m                 0.0004   1.15e-05     37.524      0.000       0.000       0.000
violent_400m                 -0.0006   1.55e-05    -37.566      0.000      -0.001      -0.001
number_of_reviews            -0.0005   4.79e-05    -11.092      0.000      -0.001      -0.000
availability_365              0.0006   1.64e-05     36.724      0.000       0.001       0.001
==============================================================================
Omnibus:                     5740.127   Durbin-Watson:                   1.892
Prob(Omnibus):                  0.000   Jarque-Bera (JB):            13016.009
Skew:                           0.714   Prob(JB):                         0.00
Kurtosis:                       5.093   Cond. No.                     1.33e+04
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 1.33e+04. This might indicate that there are
strong multicollinearity or other numerical problems.

Saved regression coefficients to: data\regression_results.csv
```

---

## 6. Analiza sieciowa (SNA)

### Hotspoty przestępczości (grid)

Tworzy:

- `data/hotspots.csv`

```
python -m network.build_hotspots
```

### Graf dwudzielny Airbnb–Hotspot

Tworzy:

- `data/bipartite_airbnb_hotspot.graphml`

```
python -m network.build_graph
```

### Miary sieciowe (centralność hotspotów)

Tworzy:

- `data/hotspot_centrality.csv`

```
python -m network.network_metrics
```

Przykład

```
python -m network.network_metrics
Reading graph: data\bipartite_airbnb_hotspot.graphml
Listings: 48645, Hotspots: 3097
Hotspot projection: 3097 nodes, 5052 edges
Saved projection graph: data\hotspot_projection.graphml
Saved: data\network_global_stats.csv
{'nodes': 3097, 'edges': 5052, 'connected_components': 894, 'largest_component_nodes': 1793, 'largest_component_edges': 4427, 'density': 0.0010537829807790986, 'avg_clustering': 0.4419103391496047}
Saved: data\hotspot_centrality.csv

Top 10 hotspots by PageRank:
                          hotspot  degree_centrality  pagerank  strength_weighted_degree  betweenness_lcc
1110             H_40.665_-73.765           0.002584  0.001086                      48.0         0.018409
2924             H_40.865_-73.925           0.002584  0.001030                     184.0         0.015422
800               H_40.635_-74.08           0.002584  0.001006                      42.0         0.000000
2254              H_40.765_-73.99           0.002584  0.001001                    1030.0         0.005647
2041               H_40.74_-73.79           0.001938  0.000998                      23.0         0.007790
2253             H_40.765_-73.985           0.002584  0.000994                     941.0         0.006211
411   H_40.595_-74.08500000000001           0.001938  0.000987                      27.0         0.000000
742                H_40.62_-74.03           0.002261  0.000983                      40.0         0.001684
1953             H_40.735_-73.955           0.002584  0.000971                     369.0         0.136286
1612              H_40.705_-74.01           0.001938  0.000967                     542.0         0.000047
```

### Community detection

Community detection (na projekcji hotspotów):
tworzy:

- `data/hotspot_projection.graphml`
- `data/hotspot_communities.csv`
- `data/community_stats.csv`
- `data/network_global_stats.csv`

```
python -m network.community_detection
```

Przykład

```
python -m network.community_detection
Reading projection graph: data\hotspot_projection.graphml
LCC: 1793 nodes, 4427 edges
Detected communities: 31
Modularity (LCC): 0.8806
Saved: data\hotspot_communities.csv
Saved: data\community_stats.csv
```

### Wizualizacje grafu

Wizualizacje grafu:
tworzy:

- `plots/6-network/hotspot_projection_top250.png`
- `plots/6-network/community_sizes.png`

```
python -m network.visualize_graph
```

Przykład

```
python -m network.visualize_graph
Saved: plots\6-network\hotspot_projection_top250.png
Saved: plots\6-network\community_sizes.png
```

Mapa społeczności (community detection) na mapie NYC:
tworzy:

- `plots/6-network/community_map.html`

```
python -m network.community_map
```

Przykład

```
python -m network.community_map
```

---
