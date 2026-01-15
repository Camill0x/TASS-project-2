from __future__ import annotations

import pandas as pd

# Minimalna taksonomia – można rozszerzać
VIOLENT = {
    "ROBBERY",
    "FELONY ASSAULT",
    "ASSAULT 3 & RELATED OFFENSES",
    "RAPE",
    "SEX CRIMES",
    "ARSON",
    "OFFENSES AGAINST THE PERSON",
}

PROPERTY = {
    "PETIT LARCENY",
    "GRAND LARCENY",
    "BURGLARY",
    "GRAND LARCENY OF MOTOR VEHICLE",
    "POSSESSION OF STOLEN PROPERTY",
    "UNAUTHORIZED USE OF A VEHICLE",
    "OTHER OFFENSES RELATED TO THEF",
}


def add_offense_group(nypd: pd.DataFrame) -> pd.DataFrame:
    """
    Dodaje kolumnę offense_group: violent / property / other.
    W oparciu o offense_description (OFNS_DESC).
    """
    df = nypd.copy()
    desc = df["offense_description"].astype(str).str.upper()

    df["offense_group"] = "other"
    df.loc[desc.isin(VIOLENT), "offense_group"] = "violent"
    df.loc[desc.isin(PROPERTY), "offense_group"] = "property"

    return df
