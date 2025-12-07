import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
import pandas as pd

from config import AIRBNB_CLEAN
from config import NYPD_CLEAN

df = pd.read_csv(NYPD_CLEAN)

gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326"
).to_crs(epsg=3857)

fig, ax = plt.subplots(figsize=(8, 8))
hb = ax.hexbin(
    gdf.geometry.x,
    gdf.geometry.y,
    gridsize=100,
    bins="log",
    cmap="magma",
)
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
plt.colorbar(hb, label="log10(count)")
ax.set_title("NYPD Complaints - gęstość na mapie")
plt.tight_layout()
plt.show()
