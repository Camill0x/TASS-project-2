# Jak napisać raport końcowy – TASS Projekt 2

Ten dokument opisuje **jak złożyć raport analityczny** na podstawie wyników wygenerowanych w projekcie.

---

## 1. Wstęp i cel projektu

- krótki opis problemu (Airbnb a bezpieczeństwo w NYC)
- uzasadnienie wyboru danych
- cel analizy

---

## 2. Źródła danych

- Airbnb NYC 2019 (Kaggle)
- NYPD Complaint Data 2018–2019 (Kaggle)
- zakres czasowy i przestrzenny

---

## 3. Technologia i pipeline

- Python, pandas, numpy
- matplotlib, folium
- scikit-learn (BallTree)
- networkx (SNA)
- automatyczny pipeline pobierania i czyszczenia danych

---

## 4. Czyszczenie i przygotowanie danych

- usunięcie braków danych
- filtrowanie współrzędnych
- normalizacja kategorii
- przygotowanie danych do modelowania (`log_price`)

---

## 5. Metodyka łączenia danych

### 5.1 Łączenie po dzielnicach (borough join)

“neighbourhood_group” (Airbnb) + “BORO_NM/borough” (NYPD)

wyniki: tabela borough_join_summary.csv + wykresy słupkowe

### 5.2 Łączenie po koordynatach (spatial join)

promień 300/400/500 m

w raporcie główne wyniki na 400 m, a 300/500 jako analiza wrażliwości

---

## 6. Analiza eksploracyjna (EDA)

- rozkłady cen
- struktura ofert
- rozkład przestępstw
- mapy gęstości (skrót)

---

## 7. Analiza przestrzenna

- mapy Folium (Airbnb vs przestępstwa)
- porównanie all / felony / violent
- hexbiny i hotspoty

w skali borough pokazujecie “makro”,

a spatial join pokazuje “mikro”.

---

## 8. Analiza statystyczna

### 8.1 Strefy przestępczości

- low / mid / high crime

  Strefy “low/mid/high crime” wyznaczono poprzez tercyle liczby przestępstw w promieniu R=400 m. Zastosowano dwie definicje stref: (1) wg przestępstw wpływających na poczucie bezpieczeństwa (violent), (2) wg kategorii prawnej felonies. Następnie porównano rozkłady cen (boxplot) oraz wartości median/średnich w każdej strefie.

- porównanie cen

(i nawet widać ciekawą rzecz: violent-zone rośnie cena lekko, a felony-zone rośnie cena mocno — to się fajnie łączy z regresją).

że robicie przekroje crime_zone x room_type i porównujecie mediany cen, opinie i dostępność.

Dodatkowo przeprowadzono analizę zależności z uwzględnieniem standardu zakwaterowania: rozbicie na room_type oraz miary aktywności oferty (number_of_reviews, reviews_per_month, availability_365). Dla każdej kategorii zakwaterowania zestawiono korelacje i porównano rozkłady cen w strefach przestępczości.

### 8.2 Korelacje

- cena vs przestępczość
- interpretacja

że pokazujecie macierz korelacji,

oraz korelacje per room_type (standard mieszkania).

### 8.3 Regresja liniowa

- model bazowy
- model rozszerzony
- interpretacja współczynników
- uwagi o multikolinearności

---

## 9. Analiza sieciowa (SNA)

### 9.1 Definicja grafu

graf dwudzielny listing–hotspot (krawędź gdy w 400 m)

projekcja hotspot–hotspot (krawędź gdy wspólny listing; waga = liczba wspólnych listingów)

### 9.2 Miary sieciowe

Wymień co policzyliście:

degree centrality

PageRank (waga)

weighted degree (strength)

betweenness (na największej składowej)

globalne: liczba składowych, gęstość, clustering, rozmiar LCC

### 9.3 Community detection

metoda: greedy modularity

wynik: liczba społeczności + modularity

interpretacja: społeczności = obszary NYC z podobnym “współdzielonym sąsiedztwem” przez oferty

### 9.4 Wizualizacje

graf top250 wg PageRank pokolorowany community

histogram rozmiarów społeczności

“community_id” przypisano hotspotom (na LCC projekcji hotspotów)

zaprezentowano na mapie NYC (Folium) – pokazuje, że community odpowiadają spójnym obszarom przestrzennym

Proponowany tekst 1:1:

Dla lepszej interpretacji wyników community detection przygotowano mapę interaktywną, w której hotspoty zostały pokolorowane zgodnie z przypisaną społecznością (community_id). Pozwala to ocenić, czy wykryte społeczności odpowiadają przestrzennie spójnym obszarom miasta (np. klastry w obrębie wybranych dzielnic).

---

## 10. Wnioski i ograniczenia

- kluczowe obserwacje
- znaczenie kategorii przestępstw
- ograniczenia danych
- możliwe kierunki dalszych badań

---

## 11. Załączniki

- mapy interaktywne (HTML)
- repozytorium
- tabele wynikowe
