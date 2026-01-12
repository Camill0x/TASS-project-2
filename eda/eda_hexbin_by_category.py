import matplotlib.pyplot as plt
import pandas as pd

from config import NYPD_CLEAN, PLOTS_DIR
from features.crime_taxonomy import add_offense_group


def hexbin_plot(df, title, output):
    plt.figure(figsize=(6, 6))
    plt.hexbin(
        df["longitude"],
        df["latitude"],
        gridsize=80,
        bins="log",
    )
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(title)
    plt.colorbar(label="log10(count)")
    plt.tight_layout()
    plt.savefig(output, dpi=200)
    plt.close()
    print(f"Saved: {output}")


def main():
    PLOTS_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(NYPD_CLEAN)

    # Felony
    felony = df[df["law_category"] == "FELONY"]
    hexbin_plot(felony, "Felony crimes – hexbin density", PLOTS_DIR / "4-2-hexbin" / "felony_hexbin.png")

    # Violent
    df = add_offense_group(df)
    violent = df[df["offense_group"] == "violent"]
    hexbin_plot(violent, "Violent crimes – hexbin density", PLOTS_DIR / "4-2-hexbin" / "violent_hexbin.png")


if __name__ == "__main__":
    main()
