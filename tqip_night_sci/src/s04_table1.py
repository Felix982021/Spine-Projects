"""Step 4: Table 1 by night vs. day with standardized mean differences."""
import numpy as np
import pandas as pd
from config import INTERIM, OUT

CONTINUOUS = ["age", "iss", "hr", "cc_count"]
CATEGORICAL = ["male", "sbp_cat", "gcs_cat", "penetrating", "sci_level",
               "sci_comp", "transport", "payer", "level", "teaching"]


def smd_continuous(x, g, w=None):
    w = np.ones(len(x)) if w is None else w
    a, b = (g == 1), (g == 0)
    m1, m0 = np.average(x[a], weights=w[a]), np.average(x[b], weights=w[b])
    v1 = np.average((x[a] - m1) ** 2, weights=w[a])
    v0 = np.average((x[b] - m0) ** 2, weights=w[b])
    return (m1 - m0) / np.sqrt((v1 + v0) / 2)


def smd_binary(x, g, w=None):
    w = np.ones(len(x)) if w is None else w
    p1 = np.average(x[g == 1], weights=w[g == 1])
    p0 = np.average(x[g == 0], weights=w[g == 0])
    denom = np.sqrt((p1 * (1 - p1) + p0 * (1 - p0)) / 2)
    return 0.0 if denom == 0 else (p1 - p0) / denom


def table1(df, w=None):
    g = df["night"].to_numpy()
    rows = []
    for v in CONTINUOUS:
        s = df[v]
        ok = s.notna().to_numpy()
        med = df.groupby("night")[v].describe()[["50%", "25%", "75%"]]
        rows.append({"variable": v,
                     "day": f"{med.loc[0, '50%']:.0f} ({med.loc[0, '25%']:.0f}-{med.loc[0, '75%']:.0f})",
                     "night": f"{med.loc[1, '50%']:.0f} ({med.loc[1, '25%']:.0f}-{med.loc[1, '75%']:.0f})",
                     "smd": smd_continuous(s.to_numpy()[ok], g[ok],
                                           None if w is None else w[ok])})
    for v in CATEGORICAL:
        s = df[v].astype("string").fillna("Missing")
        for level in sorted(s.unique()):
            x = (s == level).astype(float).to_numpy()
            n_day, n_night = int(x[g == 0].sum()), int(x[g == 1].sum())
            rows.append({"variable": f"{v}: {level}",
                         "day": f"{n_day:,} ({100 * x[g == 0].mean():.1f}%)",
                         "night": f"{n_night:,} ({100 * x[g == 1].mean():.1f}%)",
                         "smd": smd_binary(x, g, w)})
    t = pd.DataFrame(rows)
    t["smd"] = t["smd"].round(3)
    return t


if __name__ == "__main__":
    df = pd.read_parquet(INTERIM / "analytic.parquet")
    t = table1(df)
    t.to_csv(OUT / "table1.csv", index=False)
    print(t.to_string(index=False))
    # Arrivals and crude mortality by hour (for the figure)
    by_hour = df.groupby("arrival_hour").agg(n=("died", "size"), mortality=("died", "mean"))
    by_hour.to_csv(OUT / "by_hour.csv")
