from __future__ import annotations

import pandas as pd
import statsmodels.formula.api as smf

from config import DATA_DIR, DEFAULT_RADIUS_M, ROOT_DIR


def run_model(formula: str, df: pd.DataFrame, name: str) -> pd.DataFrame:
    print(f"\nRunning model: {name}")
    model = smf.ols(formula=formula, data=df).fit()
    print(model.summary())

    out = model.summary2().tables[1]
    out = out.reset_index().rename(columns={"index": "variable"})
    out["model"] = name
    return out


def main() -> None:
    path = DATA_DIR / f"merged_model_{DEFAULT_RADIUS_M}m.csv"
    print(f"Reading: {path.relative_to(ROOT_DIR)}")
    df = pd.read_csv(path)

    df["borough"] = df["neighbourhood_group"].astype("category")
    df["room_type"] = df["room_type"].astype("category")

    results = []
    fel = f"felonies_{DEFAULT_RADIUS_M}m"
    vio = f"violent_{DEFAULT_RADIUS_M}m"
    tot = f"crimes_total_{DEFAULT_RADIUS_M}m"

    # Model A
    formula_a = f"log_price ~ {tot} + borough + room_type"
    res_a = run_model(formula_a, df, "Model_A_basic")
    results.append(res_a)

    # Model B
    formula_b = f"log_price ~ {fel} + {vio} + number_of_reviews + availability_365 + borough + room_type"
    res_b = run_model(formula_b, df, "Model_B_extended")
    results.append(res_b)

    all_results = pd.concat(results, ignore_index=True)

    out_path = DATA_DIR / "regression_results.csv"
    all_results.to_csv(out_path, index=False)
    print(f"\nSaved regression coefficients to: {out_path.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
