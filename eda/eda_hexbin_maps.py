import matplotlib.pyplot as plt
import pandas as pd

from config import AIRBNB_CLEAN, NYPD_CLEAN, PLOTS_DIR


def ensure_outdir() -> None:
    outdir = PLOTS_DIR / "4-2-hexbin"
    outdir.mkdir(parents=True, exist_ok=True)


def save_hexbin(df: pd.DataFrame, title: str, output_path: str) -> None:
    plt.figure(figsize=(7, 7))
    hb = plt.hexbin(
        df["longitude"],
        df["latitude"],
        gridsize=90,
        bins="log",
    )
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(title)
    plt.colorbar(hb, label="log10(count)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Saved: {output_path}")


def main() -> None:
    ensure_outdir()
    outdir = PLOTS_DIR / "4-2-hexbin"

    airbnb = pd.read_csv(AIRBNB_CLEAN)
    nypd = pd.read_csv(NYPD_CLEAN)

    # 1) Airbnb hexbin
    save_hexbin(
        airbnb,
        "Airbnb listings – hexbin density",
        str(outdir / "airbnb_hexbin.png"),
    )

    # 2) ALL NYPD hexbin
    save_hexbin(
        nypd,
        "NYPD complaints (all categories) – hexbin density",
        str(outdir / "nypd_all_hexbin.png"),
    )

    # 3) Felony hexbin
    felony = nypd[nypd["law_category"] == "FELONY"]
    save_hexbin(
        felony,
        "NYPD Felony – hexbin density",
        str(outdir / "felony_hexbin.png"),
    )

    # 4) Violent hexbin
    from features.crime_taxonomy import add_offense_group

    nypd = add_offense_group(nypd)
    violent = nypd[nypd["offense_group"] == "violent"]
    save_hexbin(
        violent,
        "NYPD Violent-impact group – hexbin density",
        str(outdir / "violent_hexbin.png"),
    )


if __name__ == "__main__":
    main()
