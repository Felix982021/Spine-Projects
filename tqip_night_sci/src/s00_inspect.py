"""Step 0: print every column name in every file, per year, and check the
arrival time field. Run this first and fix config.COLS before anything else."""
import pandas as pd
from config import RAW, YEARS, FILES, COLS

for year in YEARS:
    for key, pattern in FILES.items():
        for path in sorted((RAW / str(year)).glob(pattern)):
            cols = list(pd.read_csv(path, nrows=0).columns)
            print(f"\n{year} {key} ({path.name}): {len(cols)} columns")
            print(", ".join(cols))

    trauma = next((RAW / str(year)).glob(FILES["trauma"]))
    header = {c.upper(): c for c in pd.read_csv(trauma, nrows=0).columns}
    col = header.get(COLS["arrival_time"].upper())
    if col is None:
        print(f"\n!! {year}: arrival time column '{COLS['arrival_time']}' not found")
        continue
    t = pd.read_csv(trauma, usecols=[col], dtype=str)[col]
    print(f"\n{year} arrival time: {t.isna().mean():.1%} missing; examples:",
          t.dropna().sample(min(10, t.notna().sum()), random_state=0).tolist())
