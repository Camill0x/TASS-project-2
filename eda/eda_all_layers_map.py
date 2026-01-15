import folium
import pandas as pd
from folium import FeatureGroup
from folium.plugins import HeatMap

from config import AIRBNB_CLEAN, NYPD_CLEAN


def add_heat_layer(m, df, name, radius=7, blur=10, gradient=None):
    fg = FeatureGroup(name=name, show=False)
    HeatMap(
        df[["latitude", "longitude"]].values.tolist(),
        radius=radius,
        blur=blur,
        gradient=gradient,
    ).add_to(fg)
    fg.add_to(m)


def main():
    airbnb = pd.read_csv(AIRBNB_CLEAN)
    nypd = pd.read_csv(NYPD_CLEAN)

    # Zróbmy też violent (na bazie Waszej taksonomii)
    from features.crime_taxonomy import add_offense_group

    nypd2 = add_offense_group(nypd)
    felony = nypd[nypd["law_category"] == "FELONY"]
    violent = nypd2[nypd2["offense_group"] == "violent"]

    m = folium.Map(location=[40.73, -73.93], zoom_start=11, tiles="cartodbpositron")

    # Warstwy (ustaw show=True tylko na jedną, żeby startowo była widoczna)
    # Airbnb – chłodny, neutralny
    add_heat_layer(
        m,
        airbnb,
        "Airbnb listings",
        radius=4,
        blur=6,
        gradient={
            0.2: "#ccece6",
            0.5: "#66c2a4",
            0.8: "#238b45",
            1.0: "#00441b",
        },
    )

    # All crimes – klasyczny heat (żółty → czerwony)
    add_heat_layer(
        m,
        nypd,
        "All crimes (NYPD)",
        radius=4,
        blur=6,
        gradient={
            0.2: "#ffffcc",
            0.4: "#ffeda0",
            0.6: "#feb24c",
            0.8: "#f03b20",
            1.0: "#bd0026",
        },
    )

    # Felony – ciemna czerwień / bordo
    add_heat_layer(
        m,
        felony,
        "Felony crimes",
        radius=4,
        blur=6,
        gradient={
            0.3: "#fee0d2",
            0.6: "#fc9272",
            0.8: "#de2d26",
            1.0: "#67000d",
        },
    )

    # Violent – wysoki kontrast (szary → czarny → czerwony)
    add_heat_layer(
        m,
        violent,
        "Violent-impact crimes",
        radius=4,
        blur=6,
        gradient={
            0.3: "#d9d9d9",
            0.6: "#636363",
            0.8: "#252525",
            1.0: "#99000d",
        },
    )

    # Layer control
    folium.LayerControl(collapsed=False).add_to(m)

    # Prosta legenda (HTML)
    legend_html = """
    <div style="
        position: fixed;
        bottom: 30px;
        left: 30px;
        width: 260px;
        z-index: 9999;
        background: white;
        padding: 12px 14px;
        border: 1px solid #ccc;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
        font-size: 13px;
        line-height: 1.4;
        ">
    <b>Legenda warstw</b><br><br>

    <div style="margin-bottom:6px;">
        <span style="display:inline-block;width:14px;height:14px;
                    background:#238b45;margin-right:8px;border-radius:3px;"></span>
        Airbnb listings
    </div>

    <div style="margin-bottom:6px;">
        <span style="display:inline-block;width:14px;height:14px;
                    background:#f03b20;margin-right:8px;border-radius:3px;"></span>
        All crimes (NYPD)
    </div>

    <div style="margin-bottom:6px;">
        <span style="display:inline-block;width:14px;height:14px;
                    background:#de2d26;margin-right:8px;border-radius:3px;"></span>
        Felony crimes
    </div>

    <div style="margin-bottom:8px;">
        <span style="display:inline-block;width:14px;height:14px;
                    background:#252525;margin-right:8px;border-radius:3px;"></span>
        Violent-impact crimes
    </div>

    <hr style="margin:8px 0;">

    <div style="color:#555; font-size:12px;">
        Kolor oznacza względne zagęszczenie punktów (HeatMap).<br>
        Warstwy można włączać i wyłączać w panelu po prawej.
    </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    output = "plots/4-1-folium/map_layers_airbnb_crime.html"
    m.save(output)
    print(f"Saved interactive layered map: {output}")


if __name__ == "__main__":
    main()
