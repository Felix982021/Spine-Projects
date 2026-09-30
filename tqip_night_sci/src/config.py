"""All paths, column names, and code lists live here. Check every column name
against the TQIP data dictionary for each year before running anything."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"            # data/raw/2017/, data/raw/2018/, ...
INTERIM = ROOT / "data" / "interim"    # parquet caches
OUT = ROOT / "output"                  # tables and figures
YEARS = [2017, 2018, 2019, 2020, 2021, 2022, 2023]

# File name patterns inside each year folder (edit to match yours)
FILES = {
    "trauma": "*TRAUMA*.csv",
    "dx": "*ICDDIAGNOSIS*.csv",
    "px": "*ICDPROCEDURE*.csv",
    "ais": "*AISDIAGNOSIS*.csv",
    "facility": "*FACILITY*.csv",
}

# Left side: the name used in our code. Right side: the name in YOUR files.
COLS = {
    "id": "INC_KEY",
    "facility": "FACILITY_KEY",
    "arrival_time": "HOSPITALARRIVALTIME",
    "age": "AGEYEARS",
    "sex": "SEX",
    "transfer": "INTERFACILITYTRANSFER",
    "signs_of_life": "SIGNSOFLIFE",
    "ed_dispo": "EDDISCHARGEDISPOSITION",
    "hosp_dispo": "HOSPDISCHARGEDISPOSITION",
    "iss": "ISS",
    "sbp": "SBP",
    "hr": "PULSERATE",
    "gcs": "TOTALGCS",
    "transport": "TRANSPORTMODE",
    "trauma_type": "TRAUMATYPE",
    "payer": "PRIMARYMETHODPAYMENT",
    "icu_days": "TOTALICULOS",
    "vent_days": "TOTALVENTDAYS",
    "los_days": "FINALDISCHARGEDAYS",
    "wlst": "WITHDRAWALLST",
    # diagnosis / procedure long files
    "dx_code": "ICDDIAGNOSISCODE",
    "px_code": "ICDPROCEDURECODE",
    "px_hours": "HOSPITALPROCEDURESTARTHRS",
    # facility file
    "level": "ACSVERIFICATIONLEVEL",
    "teaching": "TEACHINGSTATUS",
    "beds": "BEDSIZE",
}

# Codes that mean yes/no in TQIP binary fields (check the dictionary)
YES, NO = 1, 2
NO_SIGNS_OF_LIFE = 1   # value of the signs-of-life field meaning "arrived with none"

# Disposition values that mean death (fill in from the dictionary)
ED_DEATH_CODES = [5]        # e.g. "Deceased/expired" in ED disposition
HOSP_DEATH_CODES = [5]      # e.g. "Deceased/expired" in hospital disposition
HOME_CODES = [1, 2]         # home, home with services (survivors only)

# Hospital complication fields that count toward the composite
HC_FIELDS = [
    "HC_UNPLANNEDINTUBATION", "HC_VAPNEUMONIA", "HC_ARDS", "HC_AKI",
    "HC_DVTHROMBOSIS", "HC_PULMONARYEMBOLISM", "HC_MI", "HC_CARDARREST",
    "HC_STROKECVA", "HC_SEVERESEPSIS", "HC_CAUTI", "HC_CLABSI",
    "HC_PRESSUREULCER", "HC_DEEPSSI", "HC_ORGANSPACESSI",
    "HC_UNPLANNEDICU", "HC_UNPLANNEDRETURNOR",
]
CC_FIELDS = [
    "CC_DIABETES", "CC_HYPERTENSION", "CC_CHF", "CC_COPD", "CC_RENAL",
    "CC_CIRRHOSIS", "CC_ANTICOAGULANT", "CC_DEMENTIA",
    "CC_FUNCTIONALDEPENDENT", "CC_SMOKING",
]

# ICD-10-CM spinal cord injury prefixes (dots removed)
SCI_PREFIXES = ("S140", "S141", "S240", "S241", "S340", "S341")
CAUDA_PREFIXES = ("S343",)

# ICD-10-PCS spine surgery prefixes (first 4 characters)
SPINE_PX_PREFIXES = (
    "0RG0", "0RG1", "0RG2", "0RG4", "0RG6", "0RG7", "0RG8", "0RGA",
    "0SG0", "0SG1", "0SG3",
    "00NW", "00NX", "00NY", "00NT",
    "0PB3", "0PB4", "0QB0", "0QB1", "0PT3", "0PT4", "0QT0",
    "0RB3", "0RB5", "0RB9", "0RBB", "0SB2", "0SB4",
    "0RT3", "0RT5", "0RT9", "0RTB", "0ST2", "0ST4",
    "0PS3", "0PS4", "0QS0", "0QS1",
    "0RH1", "0RH4", "0RH6", "0RHA", "0SH0", "0SH3",
)

NIGHT_START_HOUR, NIGHT_END_HOUR = 18, 6   # night = 18:00 to 05:59
EARLY_SURGERY_HOURS = 24
