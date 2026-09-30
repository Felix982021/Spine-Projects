# Night arrival and outcomes after traumatic spinal cord injury (TQIP)

Starter analysis pipeline for the study protocol. TQIP files are never committed; put them in `data/raw/<year>/`.

## Setup (PyCharm)

1. Open this folder as a project and create a virtual environment (Python 3.11+).
2. `pip install -r requirements.txt`
3. Mark `src/` as Sources Root (right-click > Mark Directory as > Sources Root).
4. Copy each year's TQIP CSVs into `data/raw/2017/`, `data/raw/2018/`, and so on.

## Run order (run each from `src/`)

| Script | Does |
| --- | --- |
| `s00_inspect.py` | Lists every column per year and checks the arrival time field. Fix `config.py` first. |
| `s01_load.py` | Reads the needed columns from each year and caches them as parquet. |
| `s02_cohort.py` | Finds SCI patients, builds night vs. day, applies exclusions, writes flow counts. |
| `s03_variables.py` | Builds outcomes, spine surgery timing, covariates, hospital variables. |
| `s04_table1.py` | Table 1 with standardized mean differences; arrivals and mortality by hour. |
| `s05_models.py` | Primary GEE model, overlap-weighted model, early surgery model. |

To test without real data: `python tools/make_fake_data.py`, run the scripts, then delete `data/`.

Every column name and code value in `src/config.py` is a placeholder. Check each against the TQIP data dictionary for your years.
