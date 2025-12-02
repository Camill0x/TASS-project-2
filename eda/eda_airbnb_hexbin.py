import matplotlib.pyplot as plt
import pandas as pd

from config import AIRBNB_CLEAN, PLOTS_DIR, ROOT_DIR


def plot_airbnb_hexbin(df: pd.DataFrame) -> None:
    """Hexbin density plot of Airbnb locations in NYC."""
    plt.figure(figsize=(6, 6))
    plt.hexbin(
        df["longitude"],
        df["latitude"],
        gridsize=80,
        bins="log",
    )
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Airbnb listings - hexbin density")
    plt.colorbar(label="log10(count)")

    output_path = PLOTS_DIR / "airbnb_hexbin.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    print(f"Saved Airbnb hexbin plot to: {output_path.relative_to(ROOT_DIR)}")


def main() -> None:
    PLOTS_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(AIRBNB_CLEAN)

    plot_airbnb_hexbin(df)


if __name__ == "__main__":
    main()
