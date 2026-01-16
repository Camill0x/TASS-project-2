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

### 3.1. Agregacja przestępstw w promieniu od ofert Airbnb

Tworzy główny zbiór cech przestrzennych opartych o promień od każdej oferty airbnb:

- `data/merged_features.csv`

Zawiera m.in. liczbę przestępstw w promieniu 300 m, 400 m i 500 m.

```
python -m features.build_features_radius
```

(Czas wykonania: ok. 5 minut)

---

### 3.2. Agregacja danych w komórkach siatki przestrzennej

Tworzy zbiór zagregowanych danych przestrzennych opartych o regularną siatkę:

- `data/grid_counts_400m.csv` (rozmiar komórki: 400 m)

Zawiera liczbę ofert Airbnb oraz przestępstw NYPD (z podziałem na kategorie) w każdej komórce siatki.

```
python -m features.build_features_grid_counts
```

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
Saved: plots/5-statistical/hexbin_logprice_vs_crimes_total_400m.png
Saved: plots/5-statistical/hexbin_logprice_vs_violent_400m.png
Saved: plots/5-statistical/hexbin_logprice_vs_felonies_400m.png
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
1       Brooklyn     13141  121.311240          95.0        268702     87381        139528       41793    55962     85381
2      Manhattan     12952  181.610176         145.0        230467     72050        128594       29823    40972     98619
3         Queens      4046   93.221948          70.0        182585     57720         94791       30074    38952     59144
0          Bronx       817   79.542228          65.0        201339     55202        112821       33316    51127     52147
4  Staten Island       303   86.828383          72.0         39789      9426         21704        8659     6687      9778
Saved: plots\5-statistical\borough_airbnb_listings.png
Saved: plots\5-statistical\borough_crimes_total.png
```

### 5B. Wizualizacja agregacji w siatce przestrzennej (grid-based)

Analiza rozkładów i zależności pomiędzy liczbą ofert Airbnb a liczbą przestępstw NYPD
zagregowanych w regularnej siatce przestrzennej.

Skrypt operuje na pliku:

- `data/grid_counts_{DEFAULT_RADIUS_M}m.csv`

i tworzy wykresy eksploracyjne zapisane w:

- `plots/5-statistical/`

W szczególności generowane są:
- **hexbin (log–log)**: zależność `airbnb_count` vs `nypd_count` (gęstość komórek),
- **boxploty (log)**: rozkład liczby przestępstw NYPD w grupach komórek
  z różną liczbą ofert Airbnb.

```
python -m analysis.grid_count_visualizations
```

Tworzy:
- `hexbin_airbnb_vs_nypd_loglog_{R}m.png`
- `boxplot_nypd_by_airbnb_bins_{R}m.png`

---

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
Dep. Variable:              log_price   R-squared:                       0.511
Model:                            OLS   Adj. R-squared:                  0.511
Method:                 Least Squares   F-statistic:                     4650.
Date:                Thu, 15 Jan 2026   Prob (F-statistic):               0.00
Time:                        19:49:02   Log-Likelihood:                -19444.
No. Observations:               31177   AIC:                         3.890e+04
Df Residuals:                   31169   BIC:                         3.897e+04
Df Model:                           7
Covariance Type:            nonrobust
=============================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
---------------------------------------------------------------------------------------------
Intercept                     4.6940      0.017    278.819      0.000       4.661       4.727
borough[T.Brooklyn]           0.2556      0.016     15.651      0.000       0.224       0.288
borough[T.Manhattan]          0.5309      0.017     31.770      0.000       0.498       0.564
borough[T.Queens]             0.1478      0.018      8.427      0.000       0.113       0.182
borough[T.Staten Island]      0.0209      0.031      0.684      0.494      -0.039       0.081
room_type[T.Private room]    -0.7690      0.005   -146.416      0.000      -0.779      -0.759
room_type[T.Shared room]     -1.2082      0.017    -70.045      0.000      -1.242      -1.174
crimes_total_400m          2.298e-05   3.12e-06      7.378      0.000    1.69e-05    2.91e-05
==============================================================================
Omnibus:                     2970.616   Durbin-Watson:                   1.906
Prob(Omnibus):                  0.000   Jarque-Bera (JB):             6154.093
Skew:                           0.620   Prob(JB):                         0.00
Kurtosis:                       4.789   Cond. No.                     3.19e+04
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 3.52e+04. This might indicate that there are
strong multicollinearity or other numerical problems.

Running model: Model_B_extended
                            OLS Regression Results
==============================================================================
Dep. Variable:              log_price   R-squared:                       0.536
Model:                            OLS   Adj. R-squared:                  0.536
Method:                 Least Squares   F-statistic:                     3603.
Date:                Thu, 15 Jan 2026   Prob (F-statistic):               0.00
Time:                        19:49:02   Log-Likelihood:                -18613.
No. Observations:               31177   AIC:                         3.725e+04
Df Residuals:                   31166   BIC:                         3.734e+04
Df Model:                          10
Covariance Type:            nonrobust
=============================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
---------------------------------------------------------------------------------------------
Intercept                     4.6709      0.017    278.461      0.000       4.638       4.704
borough[T.Brooklyn]           0.2048      0.016     12.706      0.000       0.173       0.236
borough[T.Manhattan]          0.4631      0.017     27.941      0.000       0.431       0.496
borough[T.Queens]             0.0930      0.017      5.417      0.000       0.059       0.127
borough[T.Staten Island]     -0.0524      0.030     -1.755      0.079      -0.111       0.006
room_type[T.Private room]    -0.7468      0.005   -144.425      0.000      -0.757      -0.737
room_type[T.Shared room]     -1.2108      0.017    -71.819      0.000      -1.244      -1.178
felonies_400m                 0.0004   1.38e-05     29.474      0.000       0.000       0.000
violent_400m                 -0.0005   1.82e-05    -28.763      0.000      -0.001      -0.000
number_of_reviews            -0.0003   4.86e-05     -7.017      0.000      -0.000      -0.000
availability_365              0.0005   1.97e-05     27.380      0.000       0.000       0.001
==============================================================================
Omnibus:                     2787.129   Durbin-Watson:                   1.907
Prob(Omnibus):                  0.000   Jarque-Bera (JB):             5842.736
Skew:                           0.584   Prob(JB):                         0.00
Kurtosis:                       4.771   Cond. No.                     1.21e+04
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
Listings: 31177, Hotspots: 3097
Hotspot projection: 3097 nodes, 4527 edges
Saved projection graph: data/hotspot_projection.graphml
Saved: data/network_global_stats.csv
{'nodes': 3097, 'edges': 4527, 'connected_components': 1026, 'largest_component_nodes': 1621, 'largest_component_edges': 3869, 'density': 0.000944274654391722, 'avg_clustering': 0.4395082400634529}
Saved: data/hotspot_centrality.csv

Top 10 hotspots by PageRank:
                          hotspot  degree_centrality  pagerank  strength_weighted_degree  betweenness_lcc
2254              H_40.765_-73.99           0.002584  0.001210                     719.0         0.007579
1612              H_40.705_-74.01           0.001938  0.001195                     382.0         0.000965
1110             H_40.665_-73.765           0.002584  0.001191                      48.0         0.012063
800               H_40.635_-74.08           0.002261  0.001168                      39.0         0.000000
742                H_40.62_-74.03           0.002261  0.001108                      36.0         0.001863
345    H_40.58_-73.96000000000001           0.001938  0.001064                      36.0         0.002462
2924             H_40.865_-73.925           0.002584  0.001041                     120.0         0.003170
411   H_40.595_-74.08500000000001           0.001938  0.001033                      25.0         0.000000
1304             H_40.685_-73.875           0.002584  0.001011                      49.0         0.101017
1953             H_40.735_-73.955           0.002584  0.001007                     202.0         0.142355
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
LCC: 1621 nodes, 3869 edges
Detected communities: 32
Modularity (LCC): 0.8868
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
Saved: plots/6-network/community_map.html
```

### Analiza wieloskalowa sieci hotspotów (multiscale)

Analiza stabilności struktury sieciowej hotspotów dla różnych promieni agregacji przestępczości.

Skrypt:
- porównuje globalne miary sieci (gęstość, liczba komponentów, LCC, clustering),
- analizuje stabilność centralnych hotspotów (top PageRank) między skalami,
- pozwala ocenić, czy wnioski sieciowe są odporne na wybór promienia przestrzennego.

Tworzy:
- `data/multiscale_summary.csv`
- `data/multiscale_top_overlap.csv`

```
python -m network.multiscale_analysis

```

Przykład:

```
=== MULTISCALE SUMMARY (quick view) ===
 radius_m  nodes  edges  density  connected_components  largest_component_nodes  avg_clustering
      300 3097.0 1485.0 0.000310                1839.0                    294.0        0.000000
      400 3097.0 4527.0 0.000944                1026.0                   1621.0        0.439508
      500 3097.0 7891.0 0.001646                 752.0                   1986.0        0.549377

Top-10 hotspot overlaps (Jaccard):
 radius_a  radius_b  top10_jaccard  top10_intersection
      300       400       0.176471                   3
      300       500       0.176471                   3
      400       500       0.428571                   6
```

---
