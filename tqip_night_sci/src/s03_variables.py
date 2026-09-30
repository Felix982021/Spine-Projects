"""Step 3: outcomes, spine surgery timing, covariates, hospital characteristics."""
import numpy as np
import pandas as pd
from config import (INTERIM, COLS, YES, ED_DEATH_CODES, HOSP_DEATH_CODES,
                    HOME_CODES, HC_FIELDS, CC_FIELDS, SPINE_PX_PREFIXES,
                    EARLY_SURGERY_HOURS)

c = {k: v.upper() for k, v in COLS.items()}


def num(s):
    return pd.to_numeric(s, errors="coerce")


def yes(s):
    return (num(s) == YES).astype(int)


def spine_surgery(px):
    code = px[c["px_code"]].str.replace(".", "", regex=False).str.strip().str.upper()
    keep = code.str[:4].isin(SPINE_PX_PREFIXES) & (code.str[4] != "X")  # drop external approach
    px = px[keep].assign(px_hours=num(px.loc[keep, c["px_hours"]]))
    first = px.groupby(c["id"])["px_hours"].min().rename("hours_to_surgery")
    return first.reset_index()


if __name__ == "__main__":
    df = pd.read_parquet(INTERIM / "cohort.parquet")
    px = pd.read_parquet(INTERIM / "px.parquet")
    fac = pd.read_parquet(INTERIM / "facility.parquet").drop(columns="YEAR")
    fac = fac.drop_duplicates(subset=c["facility"], keep="last")

    # Outcomes
    ed_death = num(df[c["ed_dispo"]]).isin(ED_DEATH_CODES)
    hosp_death = num(df[c["hosp_dispo"]]).isin(HOSP_DEATH_CODES)
    df["died"] = (ed_death | hosp_death).astype(int)
    hc_present = [h.upper() for h in HC_FIELDS if h.upper() in df.columns]
    for h in hc_present:
        df[h] = yes(df[h])
    df["any_complication"] = df[hc_present].max(axis=1)
    df["vte"] = df[[h for h in ("HC_DVTHROMBOSIS", "HC_PULMONARYEMBOLISM")
                    if h in df.columns]].max(axis=1)
    df["home"] = np.where(df["died"] == 1, np.nan,
                          num(df[c["hosp_dispo"]]).isin(HOME_CODES).astype(float))
    for k in ("icu_days", "vent_days", "los_days"):
        df[k] = num(df[c[k]])

    # Spine surgery and timing
    df = df.merge(spine_surgery(px), on=c["id"], how="left")
    df["spine_surgery"] = df["hours_to_surgery"].notna().astype(int)
    df["early_surgery"] = np.where(df["spine_surgery"] == 1,
                                   (df["hours_to_surgery"] <= EARLY_SURGERY_HOURS).astype(float),
                                   np.nan)

    # Covariates
    df["age"] = num(df[c["age"]])
    df["male"] = (num(df[c["sex"]]) == 1).astype(int)          # check sex coding
    df["iss"] = num(df[c["iss"]])
    sbp = num(df[c["sbp"]])
    df["sbp_cat"] = pd.cut(sbp, [-1, 89, 109, 400], labels=["<90", "90-109", "110+"])
    df["hr"] = num(df[c["hr"]])
    gcs = num(df[c["gcs"]])
    df["gcs_cat"] = pd.cut(gcs, [2, 8, 12, 15], labels=["3-8", "9-12", "13-15"])
    df["penetrating"] = (num(df[c["trauma_type"]]) == 2).astype(int)  # check coding
    cc_present = [x.upper() for x in CC_FIELDS if x.upper() in df.columns]
    for x in cc_present:
        df[x] = yes(df[x])
    df["cc_count"] = df[cc_present].sum(axis=1)
    df["wlst"] = yes(df[c["wlst"]])
    for k in ("transport", "payer"):
        df[k] = df[c[k]].fillna("Missing").astype(str)

    # Hospital characteristics
    df = df.merge(fac, on=c["facility"], how="left")
    df["level"] = df[c["level"]].fillna("Missing").astype(str)
    df["teaching"] = df[c["teaching"]].fillna("Missing").astype(str)
    df["facility"] = df[c["facility"]].astype(str)

    df.to_parquet(INTERIM / "analytic.parquet", index=False)
    print(df[["died", "any_complication", "spine_surgery", "early_surgery"]].mean().round(3))
