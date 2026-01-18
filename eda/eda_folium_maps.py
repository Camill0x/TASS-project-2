import folium
import pandas as pd
from folium.plugins import HeatMap

from config import AIRBNB_CLEAN, NYPD_CLEAN


def save_map(points, center, name, output):
    m = folium.Map(location=center, zoom_start=11, tiles="cartodbpositron")
    HeatMap(points, radius=7, blur=10).add_to(m)
    m.save(output)
    print(f"Saved map: {output}")


def main():
    airbnb = pd.read_csv(AIRBNB_CLEAN)
    nypd = pd.read_csv(NYPD_CLEAN)

    center = [40.73, -73.93]

    # Airbnb
    save_map(
        airbnb[["latitude", "longitude"]].values.tolist(),
        center,
        "Airbnb",
        "plots/4-1-folium/map_airbnb.html",
    )

    # All crimes
    save_map(
        nypd[["latitude", "longitude"]].values.tolist(),
        center,
        "All crimes",
        "plots/4-1-folium/map_crimes_all.html",
    )

    # Felony
    felony = nypd[nypd["law_category"] == "FELONY"]
    save_map(
        felony[["latitude", "longitude"]].values.tolist(),
        center,
        "Felony",
        "plots/4-1-folium/map_crimes_felony.html",
    )

    # Violent
    from features.crime_taxonomy import add_offense_group

    nypd = add_offense_group(nypd)
    violent = nypd[nypd["offense_group"] == "violent"]

    save_map(
        violent[["latitude", "longitude"]].values.tolist(),
        center,
        "Violent crimes",
        "plots/4-1-folium/map_crimes_violent.html",
    )


if __name__ == "__main__":
    main()
