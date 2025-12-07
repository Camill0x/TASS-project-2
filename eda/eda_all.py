import folium
from folium import FeatureGroup
from folium.plugins import HeatMap
import pandas as pd
from config import AIRBNB_CLEAN, NYPD_CLEAN

airbnb = pd.read_csv(AIRBNB_CLEAN)
nypd = pd.read_csv(NYPD_CLEAN)

m = folium.Map(location=[40.73, -73.93], zoom_start=11, tiles="cartodbpositron")

# Warstwa Airbnb
heat_airbnb = HeatMap(
    airbnb[["latitude", "longitude"]], radius=7, blur=10, name="Airbnb"
)
# Warstwa NYPD
heat_nypd = HeatMap(
    nypd[["latitude", "longitude"]], radius=7, blur=10, name="NYPD", gradient={0.4:"blue", 0.65:"orange", 1:"red"}
)

folium.FeatureGroup(name="Airbnb").add_child(heat_airbnb).add_to(m)
folium.FeatureGroup(name="NYPD").add_child(heat_nypd).add_to(m)

folium.LayerControl().add_to(m)
m.save("plots/nyc_airbnb_crime.html")
