"""Writes small fake TQIP-style files to data/raw/ so you can test the pipeline
before touching real data. Delete data/raw/ afterwards."""
import numpy as np, pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rng=np.random.default_rng(1)
sci_codes=["S14114A","S14125A","S14107A","S140XXA","S24112A","S24154A","S34111A","S34124A","S343XXA","S12.100A"]
for y in range(2017,2024):
    d=ROOT/"data"/"raw"/str(y); d.mkdir(parents=True,exist_ok=True)
    n=1500; ids=np.arange(n)+y*100000
    hour=rng.integers(0,24,n); minute=rng.integers(0,60,n)
    fmt = (lambda h,m: f"{h:02d}:{m:02d}") if y%2 else (lambda h,m: f"{h:02d}{m:02d}")
    at=[fmt(h,m) for h,m in zip(hour,minute)]
    at=[a if rng.random()>0.03 else "" for a in at]
    night=((hour>=18)|(hour<6)).astype(int)
    iss=rng.integers(1,50,n)
    p=1/(1+np.exp(-(-4+0.06*iss+0.2*night)))
    died=rng.random(n)<p
    tr=pd.DataFrame({"inc_key" if y>2020 else "INC_KEY":ids,"FACILITY_KEY":rng.integers(1,60,n),
      "HOSPITALARRIVALTIME":at,"AGEYEARS":rng.integers(12,90,n),"SEX":rng.integers(1,3,n),
      "INTERFACILITYTRANSFER":rng.choice([1,2],n,p=[.3,.7]),"SIGNSOFLIFE":rng.choice([1,2],n,p=[.02,.98]),
      "EDDISCHARGEDISPOSITION":np.where(died&(rng.random(n)<.2),5,1),
      "HOSPDISCHARGEDISPOSITION":np.where(died,5,rng.choice([1,2,3,4],n)),
      "ISS":iss,"SBP":rng.normal(125,25,n).round(),"PULSERATE":rng.normal(90,20,n).round(),
      "TOTALGCS":rng.integers(3,16,n),"TRANSPORTMODE":rng.choice([1,2,3],n),"TRAUMATYPE":rng.choice([1,2],n,p=[.9,.1]),
      "PRIMARYMETHODPAYMENT":rng.choice([1,2,3,4],n),"TOTALICULOS":rng.integers(0,20,n),"TOTALVENTDAYS":rng.integers(0,10,n),
      "FINALDISCHARGEDAYS":rng.integers(1,40,n),"WITHDRAWALLST":rng.choice([1,2],n,p=[.05,.95])})
    for h in ["HC_DVTHROMBOSIS","HC_PULMONARYEMBOLISM","HC_PRESSUREULCER","HC_ARDS"]:
        tr[h]=rng.choice([1,2],n,p=[.05,.95])
    for cc in ["CC_DIABETES","CC_HYPERTENSION","CC_ANTICOAGULANT"]:
        tr[cc]=rng.choice([1,2],n,p=[.2,.8])
    tr.to_csv(d/"PUF_TRAUMA.csv",index=False)
    dx=pd.DataFrame({"INC_KEY":np.repeat(ids,2),"ICDDIAGNOSISCODE":rng.choice(sci_codes,2*n)})
    dx.to_csv(d/"PUF_ICDDIAGNOSIS.csv",index=False)
    has=rng.random(n)<.5
    px=pd.DataFrame({"INC_KEY":ids[has],"ICDPROCEDURECODE":rng.choice(["0RG10A0","00NW0ZZ","0PS3XZZ","0SG00A1","5A1955Z"],has.sum()),
                     "HOSPITALPROCEDURESTARTHRS":rng.gamma(2,15,has.sum()).round(1)})
    px.to_csv(d/"PUF_ICDPROCEDURE.csv",index=False)
    fac=pd.DataFrame({"FACILITY_KEY":np.arange(1,60),"ACSVERIFICATIONLEVEL":rng.choice([1,2],59),
                      "TEACHINGSTATUS":rng.choice(["University","Community"],59),"BEDSIZE":rng.choice([1,2,3],59)})
    fac.to_csv(d/"TQIP_FACILITY.csv",index=False)
