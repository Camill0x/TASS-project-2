# TASS Projekt 2 – Etap 2

## Plan realizacji analizy i raportu (krok po kroku)

Ten dokument opisuje **dokładne kroki**, które należy wykonać na bazie obecnego kodu z Etapu 1, aby:

- zrealizować **Etap 2 projektu**,
- uwzględnić **uwagi prowadzącego**,
- zachować spójność z przedmiotem **Techniki Analizy Sieci Społecznych**,
- przygotować **spójny raport analityczny**.

---

## 0. Uporządkowanie repozytorium

### Stan obecny (Etap 1 – OK)

- `utils/download_dataset.py`
- `utils/clean_dataset.py`
- `eda/*`
- `config.py`

### Struktura docelowa (Etap 2)

```
features/    # łączenie danych, cechy przestrzenne
analysis/    # statystyka, regresje, wykresy końcowe
network/     # analiza sieciowa (networkx)
report/      # raport końcowy (markdown/docx/pdf)
data/        # csv pośrednie i wynikowe
plots/       # wykresy i mapy
```

---

## 1. Pipeline danych (utrwalenie Etapu 1)

### 1.1 Minimalne poprawki czyszczenia

- Po `pd.to_datetime(..., errors="coerce")` **usunąć rekordy z NaT**
- Dopiero potem filtrować lata 2018–2019

### 1.2 Dataset „model-ready”

Nie modyfikować `*_clean.csv`.  
Dodać etap:

- obcięcie outlierów ceny (np. `price <= 1000`)
- `log_price = log1p(price)`
- uzupełnienie `reviews_per_month = 0`

Wynik: dane gotowe do analiz statystycznych.

---

## 2. Kategorie przestępstw (uwaga prowadzącego)

### 2.1 Warstwa A – kategorie prawne (LAW_CAT_CD)

- FELONY
- MISDEMEANOR
- VIOLATION

Zliczane osobno dla każdej oferty Airbnb.

### 2.2 Warstwa B – wpływ na poczucie bezpieczeństwa

Na podstawie `OFNS_DESC`:

- **violent** – rozboje, gwałty, zabójstwa, felony assault
- **property** – burglary, larceny
- **other / minor** – harassment, mischief

To uzasadnia analizę „realnego bezpieczeństwa”, a nie tylko liczby zgłoszeń.

---

## 3. Łączenie przestrzenne danych (rdzeń projektu)

### 3.1 Spatial join po promieniu

- brak wspólnego ID → łączenie po współrzędnych GPS
- promień: **400 m** (dodatkowo 300 i 500 m do porównań)

Dla każdej oferty Airbnb policzyć:

- `crimes_total`
- `felonies_nearby`
- `misdemeanors_nearby`
- `violations_nearby`
- `violent_nearby`
- `property_nearby`

Wynik: `data/merged_features.csv`

---

## 4. Etap 2 – analiza przestrzenna

### 4.1 Mapy (Folium)

Osobne mapy:

1. Airbnb (HeatMap)
2. Wszystkie przestępstwa
3. Felony
4. Violent crimes

Format:

- interaktywne `.html`
- screenshoty do raportu

### 4.2 Porównania gęstości

- hexbin Airbnb
- hexbin felony
- hexbin violent

Krótka interpretacja pokrywania się hotspotów.

---

## 5. Etap 3 – analiza statystyczna

### 5.1 Standard mieszkania (uwaga prowadzącego)

W analizach jawnie użyć:

- `price`, `log_price`
- `room_type`
- `number_of_reviews`
- `reviews_per_month`
- `availability_365`

### 5.2 Strefy przestępczości

Podział ofert na:

- low / mid / high crime  
  (tercyle na podstawie `violent_nearby` lub `felonies_nearby`)

Wykresy:

- boxplot ceny
- boxplot log(ceny)

### 5.3 Korelacje

- `log_price` vs `violent_nearby`
- `log_price` vs `felonies_nearby`
- opcjonalnie heatmapa korelacji

### 5.4 Regresja liniowa

Model bazowy:

```
log_price ~ crimes_total + borough + room_type
```

Model rozszerzony:

```
log_price ~ felonies_nearby + violent_nearby +
            borough + room_type +
            number_of_reviews + availability_365
```

Interpretacja kluczowych współczynników.

---

## 6. Część sieciowa (Techniki Analizy Sieci Społecznych)

### 6.1 Hotspoty jako węzły

- agregacja przestępstw do gridu (np. 0.005°)
- każda komórka = hotspot

### 6.2 Graf dwudzielny

- węzły: Airbnb listings + hotspoty
- krawędź: listing w promieniu R od hotspotu
- waga: liczba violent / felony w hotspotie

### 6.3 Miary sieciowe (networkx)

- degree / weighted degree
- PageRank / eigenvector centrality
- top hotspoty
- (opcjonalnie) community detection

### 6.4 Połączenie sieci i standardu

- czy droższe oferty są mniej „centralne” względem violent hotspotów?
- czy centralność hotspotu koreluje z cenami w jego otoczeniu?

---

## 7. Propozycja struktury raportu końcowego

### 1. Wstęp i cel analizy

### 2. Źródła danych i zakres czasowy

### 3. Technologia i pipeline przetwarzania

### 4. Czyszczenie i przygotowanie danych

### 5. Metodyka łączenia danych (borough + spatial join)

### 6. Analiza eksploracyjna (Etap 1 – skrót)

### 7. Analiza przestrzenna (Etap 2)

### 8. Analiza statystyczna (Etap 3)

### 9. Analiza sieciowa (SNA)

### 10. Wnioski i ograniczenia

### 11. Załączniki (mapy HTML, repozytorium)

---

**Ten dokument może być używany jako checklist oraz jako baza do raportu końcowego.**
