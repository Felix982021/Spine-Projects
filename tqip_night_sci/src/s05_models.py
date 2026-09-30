"""Step 5: primary GEE model and overlap-weighted propensity analysis."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from config import INTERIM, OUT
from s04_table1 import table1

COVARIATES = ("bs(age, df=4) + male + bs(iss, df=4) + C(sbp_cat) + hr + C(gcs_cat)"
              " + penetrating + C(sci_level) + C(sci_comp) + cc_count"
              " + C(transport) + C(payer) + C(level) + C(teaching) + C(YEAR)")


def gee_logit(formula, data):
    data = data.sort_values("facility")
    model = smf.gee(formula, groups="facility", data=data,
                    family=sm.families.Binomial(),
                    cov_struct=sm.cov_struct.Exchangeable())
    return model.fit()


def odds_ratio(fit, term="night"):
    ci = fit.conf_int().loc[term]
    return {"OR": np.exp(fit.params[term]), "lo": np.exp(ci[0]),
            "hi": np.exp(ci[1]), "p": fit.pvalues[term]}


def overlap_weights(data):
    ps_fit = smf.logit("night ~ " + COVARIATES, data=data).fit(disp=0)
    ps = ps_fit.predict(data)
    w = np.where(data["night"] == 1, 1 - ps, ps)
    return w, ps


if __name__ == "__main__":
    df = pd.read_parquet(INTERIM / "analytic.parquet")
    needed = ["died", "night", "age", "male", "iss", "sbp_cat", "hr", "gcs_cat",
              "penetrating", "sci_level", "sci_comp", "cc_count", "transport",
              "payer", "level", "teaching", "YEAR", "facility"]
    cc = df.dropna(subset=needed).copy()   # complete case first; swap in MICE later
    print(f"Complete cases: {len(cc):,} of {len(df):,}")

    results = []
    fit = gee_logit("died ~ night", cc)
    results.append({"model": "Unadjusted GEE", **odds_ratio(fit)})
    fit = gee_logit("died ~ night + " + COVARIATES, cc)
    results.append({"model": "Adjusted GEE (primary)", **odds_ratio(fit)})

    w, ps = overlap_weights(cc)
    cc["ow"] = w
    balance = table1(cc, w=cc["ow"].to_numpy())
    balance.to_csv(OUT / "balance_overlap_weights.csv", index=False)
    print("Max |SMD| after weighting:", balance["smd"].abs().max())
    cc = cc.sort_values("facility")
    wfit = smf.gee("died ~ night", groups="facility", data=cc, weights=cc["ow"],
                   family=sm.families.Binomial(),
                   cov_struct=sm.cov_struct.Independence()).fit()
    results.append({"model": "Overlap-weighted", **odds_ratio(wfit)})

    surg = cc[cc["spine_surgery"] == 1]
    fit = gee_logit("early_surgery ~ night + " + COVARIATES, surg)
    results.append({"model": "Early surgery, adjusted GEE", **odds_ratio(fit)})

    out = pd.DataFrame(results).round(4)
    out.to_csv(OUT / "main_results.csv", index=False)
    print(out.to_string(index=False))
