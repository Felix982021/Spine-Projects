"""Step 1: read each year's CSVs, keep only what we need, stack years, cache as parquet."""
import pandas as pd
from config import RAW, INTERIM, YEARS, FILES, COLS, HC_FIELDS, CC_FIELDS


def find_file(year, key):
    matches = sorted((RAW / str(year)).glob(FILES[key]))
    if len(matches) != 1:
        raise FileNotFoundError(f"{year} {key}: expected 1 file, found {matches}")
    return matches[0]


def read_year(year, key, wanted):
    path = find_file(year, key)
    header = pd.read_csv(path, nrows=0).columns
    upper = {c.upper(): c for c in header}          # names change case across years
    present = [upper[w.upper()] for w in wanted if w.upper() in upper]
    missing = [w for w in wanted if w.upper() not in upper]
    if missing:
        print(f"  {year} {key}: missing columns {missing}")
    df = pd.read_csv(path, usecols=present, dtype=str, low_memory=False)
    df.columns = [c.upper() for c in df.columns]
    df["YEAR"] = year
    return df


def stack(key, wanted):
    frames = [read_year(y, key, wanted) for y in YEARS]
    out = pd.concat(frames, ignore_index=True)
    out.to_parquet(INTERIM / f"{key}.parquet", index=False)
    print(f"{key}: {len(out):,} rows")
    return out


if __name__ == "__main__":
    INTERIM.mkdir(parents=True, exist_ok=True)
    c = COLS
    trauma_cols = [c[k] for k in ("id", "facility", "arrival_time", "age", "sex",
                   "transfer", "signs_of_life", "ed_dispo", "hosp_dispo", "iss",
                   "sbp", "hr", "gcs", "transport", "trauma_type", "payer",
                   "icu_days", "vent_days", "los_days", "wlst")]
    stack("trauma", trauma_cols + HC_FIELDS + CC_FIELDS)
    stack("dx", [c["id"], c["dx_code"]])
    stack("px", [c["id"], c["px_code"], c["px_hours"]])
    stack("facility", [c["facility"], c["level"], c["teaching"], c["beds"]])
