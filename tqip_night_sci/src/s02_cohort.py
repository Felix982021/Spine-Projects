"""Step 2: find SCI patients, derive level/completeness, build the exposure,
apply exclusions in order, and log counts for the STROBE flow diagram."""
import numpy as np
import pandas as pd
from config import (INTERIM, OUT, COLS, YES, NO_SIGNS_OF_LIFE, SCI_PREFIXES, CAUDA_PREFIXES,
                    NIGHT_START_HOUR, NIGHT_END_HOUR)

c = {k: v.upper() for k, v in COLS.items()}


def clean_code(s):
    return s.str.replace(".", "", regex=False).str.strip().str.upper()


def parse_minutes(t):
    """Clock time text -> minutes after midnight (0-1439), else NaN.
    Handles 'HH:MM', 'HH:MM:SS', 'HHMM', 'HMM', and a bare hour 'H'/'HH'."""
    s = t.astype("string").str.strip()
    hhmm = s.str.extract(r"^(\d{1,2}):(\d{2})(?::\d{2})?$")
    digits = s.str.extract(r"^(\d{3,4})$")[0].str.zfill(4)
    hour_only = s.str.extract(r"^(\d{1,2})$")[0]
    h = pd.to_numeric(hhmm[0], errors="coerce")
    m = pd.to_numeric(hhmm[1], errors="coerce")
    h = h.fillna(pd.to_numeric(digits.str[:2], errors="coerce"))
    m = m.fillna(pd.to_numeric(digits.str[2:], errors="coerce"))
    h = h.fillna(pd.to_numeric(hour_only, errors="coerce"))
    m = m.where(h.isna() | m.notna(), 0)          # bare hour -> minute 0
    ok = h.between(0, 23) & m.between(0, 59)
    return (h * 60 + m).where(ok)


def sci_features(dx):
    dx = dx.assign(code=clean_code(dx[c["dx_code"]]))
    sci = dx[dx["code"].str.startswith(SCI_PREFIXES + CAUDA_PREFIXES, na=False)].copy()
    code = sci["code"]
    # level: lower number = higher (worse) level
    lvl = np.select(
        [code.str.match(r"^S141\d[1-4]"), code.str.match(r"^S141\d[5-8]"),
         code.str.startswith(("S140", "S141")), code.str.startswith(("S240", "S241")),
         code.str.startswith(("S340", "S341")), code.str.startswith("S343")],
        [1, 2, 3, 4, 5, 6], 9)
    # completeness: lower number = more severe
    comp = np.select(
        [code.str.match(r"^S(14|24|34)11"), code.str.startswith("S1412"),
         code.str.match(r"^S(141[345]|241[345]|3412)"),
         code.str.startswith(("S140", "S240", "S340"))],
        [1, 2, 3, 4], 5)
    sci = sci.assign(level=lvl, comp=comp,
                     cord=code.str.startswith(SCI_PREFIXES),
                     cauda=code.str.startswith(CAUDA_PREFIXES))
    g = sci.groupby(c["id"]).agg(level=("level", "min"), comp=("comp", "min"),
                                cord=("cord", "any"), cauda_only=("cauda", "all"))
    g["sci_level"] = g["level"].map({1: "C1-C4", 2: "C5-C8", 3: "Cervical NOS",
                                    4: "Thoracic", 5: "Lumbar", 6: "Cauda equina"})
    g["sci_comp"] = g["comp"].map({1: "Complete", 2: "Central cord",
                                  3: "Other incomplete", 4: "Concussion/edema",
                                  5: "Unspecified"})
    return g.reset_index()


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    tr = pd.read_parquet(INTERIM / "trauma.parquet")
    dx = pd.read_parquet(INTERIM / "dx.parquet")
    flow = []

    def log(label, df):
        flow.append((label, len(df)))
        print(f"{label:<45}{len(df):>10,}")

    sci = sci_features(dx)
    df = tr.merge(sci, on=c["id"], how="inner")
    df["cauda_only"] = df["cauda_only"].astype(bool)
    log("SCI or cauda equina code", df)
    df = df[~df["cauda_only"]]                 # cauda-only patients: sensitivity only
    log("Spinal cord injury code", df)

    age = pd.to_numeric(df[c["age"]], errors="coerce")
    df = df[age >= 18]
    log("Age 18 or older", df)
    df = df[pd.to_numeric(df[c["transfer"]], errors="coerce") != YES]
    log("Not transferred in", df)

    df["arrival_min"] = parse_minutes(df[c["arrival_time"]])
    df = df[df["arrival_min"].notna()]
    log("Valid arrival time", df)
    df = df[pd.to_numeric(df[c["signs_of_life"]], errors="coerce") != NO_SIGNS_OF_LIFE]
    log("Signs of life on arrival", df)
    df = df[df[c["hosp_dispo"]].notna() | df[c["ed_dispo"]].notna()]
    log("Known discharge disposition", df)
    iss = pd.to_numeric(df[c["iss"]], errors="coerce")
    df = df[iss > 0]
    log("ISS recorded and above 0", df)

    df["arrival_hour"] = (df["arrival_min"] // 60).astype(int)
    df["night"] = ((df["arrival_hour"] >= NIGHT_START_HOUR) |
                   (df["arrival_hour"] < NIGHT_END_HOUR)).astype(int)

    pd.DataFrame(flow, columns=["step", "n"]).to_csv(OUT / "flow_counts.csv", index=False)
    df.to_parquet(INTERIM / "cohort.parquet", index=False)
    print(df["night"].value_counts())
