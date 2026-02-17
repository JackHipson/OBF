"""
bb_forecast_new.py - Oakbrook Backbook Forecast Model v2
========================================================
Built from scratch. Reads Fact_Raw_New.xlsx and Rate_Methodology.csv.
Produces a 40-month forecast (Oct-25 → Jan-29) with full impairment.

Usage:
    python bb_forecast_new.py [--months 40] [--output output_new]
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import argparse
from calendar import monthrange

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════
# 1. CONFIGURATION
# ════════════════════════════════════════════════════════════

class Config:
    MAX_MONTHS = 40
    MOB_THRESHOLD = 3          # min MOB for rate calc (skip early noise)
    DEFAULT_LOOKBACK = 6

    SEGMENTS = ["NON PRIME", "NRP-S", "NRP-M", "NRP-L", "PRIME"]

    # Loansize → NRP sub-segment mapping (Near Prime only)
    LOANSIZE_MAP = {
        "£0-£5k":   "NRP-S",
        "£5k-£10k": "NRP-M",
        "£10K-£15k": "NRP-M",
        "£15-£20k":  "NRP-L",
    }

    # Cohort clustering boundaries: (start_inclusive, end_exclusive) → cluster_id
    # Anything >= 202404 stays monthly
    CLUSTER_MONTHLY_FROM = 202404
    COHORT_CLUSTERS = [
        (None,   202001, 201912),   # Pre-2020 → 201912
        (202001, 202101, 202001),   # Jan-20 to Dec-20 → 202001
        (202101, 202209, 202101),   # Jan-21 to Aug-22 → 202101
        (202209, 202306, 202201),   # Sep-22 to May-23 → 202201
        (202306, 202404, 202301),   # Jun-23 to Mar-24 → 202301
    ]

    # Rate caps (min, max).  Manual approach bypasses these.
    RATE_CAPS = {
        "Coll_Principal":              (-0.50,  0.15),
        "Coll_Interest":               (-0.20,  0.05),
        "InterestRevenue":             ( 0.00,  0.50),
        "WO_DebtSold":                 ( 0.00,  0.20),
        "WO_Other":                    ( 0.00,  0.05),
        "ContraSettlements_Principal":  (-0.15,  0.01),
        "ContraSettlements_Interest":   (-0.01,  0.01),
        "Total_Coverage_Ratio":         ( 0.00,  2.50),
        "Debt_Sale_Coverage_Ratio":     ( 0.50,  1.00),
        "Debt_Sale_Proceeds_Rate":      ( 0.10,  1.00),
    }

    DEBT_SALE_MONTHS = [3, 6, 9, 12]   # Mar, Jun, Sep, Dec

    # Metrics whose rates are applied to OpeningGBV to get monthly amounts
    FLOW_METRICS = [
        "Coll_Principal", "Coll_Interest", "InterestRevenue",
        "WO_DebtSold", "WO_Other",
        "ContraSettlements_Principal", "ContraSettlements_Interest",
    ]

    # Impairment metrics (ratios, not flow amounts)
    IMPAIRMENT_METRICS = [
        "Total_Coverage_Ratio",
        "Debt_Sale_Coverage_Ratio",
        "Debt_Sale_Proceeds_Rate",
    ]


# ════════════════════════════════════════════════════════════
# 2. DATA LOADING & TRANSFORMATION
# ════════════════════════════════════════════════════════════

def _ym_to_date(ym: int) -> pd.Timestamp:
    """Convert YYYYMM integer to end-of-month Timestamp."""
    y, m = divmod(int(ym), 100)
    return pd.Timestamp(y, m, monthrange(y, m)[1])


def _cluster_cohort(raw_cohort) -> int:
    """Map a raw cohort value to its cluster representative YYYYMM."""
    if isinstance(raw_cohort, str) and "pre" in raw_cohort.lower():
        return 201912
    try:
        c = int(raw_cohort)
    except (ValueError, TypeError):
        return 201912  # fallback

    if c >= Config.CLUSTER_MONTHLY_FROM:
        return c
    for lo, hi, cluster_id in Config.COHORT_CLUSTERS:
        if lo is None:
            if c < hi:
                return cluster_id
        elif lo <= c < hi:
            return cluster_id
    return c  # shouldn't happen but keep original


def _assign_segment(lob: str, loansize: str) -> str:
    """Map (lob, loansize) to model segment."""
    if lob == "Non Prime":
        return "NON PRIME"
    if lob == "Prime":
        return "PRIME"
    if lob == "Near Prime":
        return Config.LOANSIZE_MAP.get(loansize, "NRP-M")
    return "UNKNOWN"


def load_and_transform(xlsx_path: str) -> pd.DataFrame:
    """Load Fact_Raw_New.xlsx, rename columns, create Segment, cluster cohorts, compute MOB."""
    log.info("Loading %s ...", xlsx_path)
    raw = pd.read_excel(xlsx_path)
    log.info("  Loaded %d rows × %d cols", len(raw), len(raw.columns))

    # Segment assignment
    raw["Segment"] = raw.apply(lambda r: _assign_segment(r["lob"], r["loansize"]), axis=1)

    # Cohort clustering
    raw["Cohort"] = raw["cohort"].apply(_cluster_cohort)

    # Calendar month → end-of-month date
    raw["CalendarMonth"] = raw["calendarmonth"].apply(_ym_to_date)

    # Days in month (for interest revenue annualisation)
    raw["DaysInMonth"] = raw["CalendarMonth"].apply(lambda d: d.day)

    # MOB = months between cluster cohort and calendar month
    def _mob(row):
        cy, cm = divmod(int(row["calendarmonth"]), 100)
        ky, km = divmod(int(row["Cohort"]), 100)
        return (cy * 12 + cm) - (ky * 12 + km)
    raw["MOB"] = raw.apply(_mob, axis=1)

    # Rename columns to model names
    rename = {
        "openinggbv":                  "OpeningGBV",
        "principalcollections":        "Coll_Principal",
        "interestcollections":         "Coll_Interest",
        "interestrevenue":             "InterestRevenue",
        "debtsalewriteoffs":           "WO_DebtSold",
        "otherwriteoffs":              "WO_Other",
        "principalcontrasettlement":   "ContraSettlements_Principal",
        "nonprincipalcontrasettlement":"ContraSettlements_Interest",
        "closinggbv":                  "ClosingGBV",
        "provisionatmonthend":         "Provision_Balance",
        "debtsaleproceeds":            "Debt_Sale_Proceeds",
    }
    raw.rename(columns=rename, inplace=True)

    # Fill NaN numerics with 0
    num_cols = list(rename.values()) + ["DaysInMonth", "MOB"]
    for c in num_cols:
        if c in raw.columns:
            raw[c] = pd.to_numeric(raw[c], errors="coerce").fillna(0)

    # Filter to MOB >= 0
    raw = raw[raw["MOB"] >= 0].copy()

    log.info("  Segments: %s", sorted(raw["Segment"].unique()))
    log.info("  Cohorts (clustered): %d unique", raw["Cohort"].nunique())
    log.info("  CalendarMonth range: %s → %s",
             raw["CalendarMonth"].min().strftime("%Y-%m"),
             raw["CalendarMonth"].max().strftime("%Y-%m"))
    return raw


def aggregate_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to Segment × Cohort × CalendarMonth level."""
    log.info("Aggregating to Segment × Cohort × CalendarMonth ...")
    amount_cols = [
        "OpeningGBV", "Coll_Principal", "Coll_Interest", "InterestRevenue",
        "WO_DebtSold", "WO_Other", "ContraSettlements_Principal",
        "ContraSettlements_Interest", "ClosingGBV", "Provision_Balance",
        "Debt_Sale_Proceeds",
    ]
    agg_dict = {c: "sum" for c in amount_cols}
    agg_dict["DaysInMonth"] = "first"   # same for all rows in a calendar month
    agg_dict["MOB"] = "first"           # same within cluster + calmonth

    df = (raw.groupby(["Segment", "Cohort", "CalendarMonth"], as_index=False)
             .agg(agg_dict))

    # Recompute MOB properly from Cohort and CalendarMonth
    def _mob_from_dates(row):
        cm = row["CalendarMonth"]
        ky, km = divmod(int(row["Cohort"]), 100)
        return (cm.year * 12 + cm.month) - (ky * 12 + km)
    df["MOB"] = df.apply(_mob_from_dates, axis=1)

    df.sort_values(["Segment", "Cohort", "CalendarMonth"], inplace=True)
    log.info("  Aggregated to %d rows", len(df))
    return df


# ════════════════════════════════════════════════════════════
# 3. HISTORICAL RATE CURVES
# ════════════════════════════════════════════════════════════

def compute_historical_curves(agg: pd.DataFrame) -> pd.DataFrame:
    """Compute rate curves from aggregated actuals, indexed by Segment × Cohort × MOB."""
    log.info("Computing historical rate curves ...")
    df = agg.copy()

    # Safe divide helper
    def _sdiv(num, den):
        return np.where(den.abs() > 1, num / den, 0.0)

    # Flow rates (monthly, as fraction of OpeningGBV)
    for metric in ["Coll_Principal", "Coll_Interest", "WO_DebtSold", "WO_Other",
                    "ContraSettlements_Principal", "ContraSettlements_Interest"]:
        df[f"{metric}_Rate"] = _sdiv(df[metric], df["OpeningGBV"])

    # Interest revenue: annualise
    df["InterestRevenue_Rate"] = _sdiv(df["InterestRevenue"], df["OpeningGBV"]) * (365.0 / df["DaysInMonth"].clip(lower=28))

    # Coverage ratio (provision is negative in raw data, so negate)
    df["Total_Coverage_Ratio"] = _sdiv(-df["Provision_Balance"], df["ClosingGBV"])
    df["Total_Coverage_Ratio"] = df["Total_Coverage_Ratio"].clip(lower=0)

    # Debt sale ratios (only meaningful in debt sale months)
    has_ds = df["WO_DebtSold"].abs() > 1
    df["Debt_Sale_Coverage_Ratio"] = 0.0
    df["Debt_Sale_Proceeds_Rate"] = 0.0
    # For debt sale months, approximate DS coverage as a fixed proportion
    # (we don't have explicit DS provision release in raw data, use 0.785 default)
    df.loc[has_ds, "Debt_Sale_Coverage_Ratio"] = 0.785
    df.loc[has_ds, "Debt_Sale_Proceeds_Rate"] = _sdiv(
        df.loc[has_ds, "Debt_Sale_Proceeds"],
        df.loc[has_ds, "WO_DebtSold"]
    )

    # Collapse to Segment × Cohort × MOB (take mean if multiple calmonths map to same MOB)
    rate_cols = [f"{m}_Rate" for m in Config.FLOW_METRICS] + Config.IMPAIRMENT_METRICS
    group_cols = ["Segment", "Cohort", "MOB"]

    curves = (df.groupby(group_cols, as_index=False)
                .agg({**{c: "mean" for c in rate_cols},
                      "OpeningGBV": "sum"}))

    curves.sort_values(group_cols, inplace=True)
    log.info("  Curves: %d rows across %d segment×cohort combos",
             len(curves), curves.groupby(["Segment","Cohort"]).ngroups)
    return curves


# ════════════════════════════════════════════════════════════
# 4. RATE METHODOLOGY LOOKUP
# ════════════════════════════════════════════════════════════

def load_methodology(csv_path: str) -> pd.DataFrame:
    """Load Rate_Methodology.csv."""
    log.info("Loading methodology from %s", csv_path)
    meth = pd.read_csv(csv_path)
    meth["Segment"] = meth["Segment"].fillna("ALL").astype(str).str.strip()
    meth["Cohort"]  = meth["Cohort"].fillna("ALL").astype(str).str.replace(".0", "", regex=False).str.strip()
    meth["Metric"]  = meth["Metric"].fillna("ALL").astype(str).str.strip()
    meth["MOB_Start"] = pd.to_numeric(meth["MOB_Start"], errors="coerce").fillna(0).astype(int)
    meth["MOB_End"]   = pd.to_numeric(meth["MOB_End"], errors="coerce").fillna(999).astype(int)
    meth["Approach"]  = meth["Approach"].astype(str).str.strip()
    meth["Param1"]    = meth["Param1"].astype(str).str.replace(".0", "", regex=False).str.strip()
    meth["Param2"]    = meth["Param2"].astype(str).str.strip()
    log.info("  Loaded %d methodology rules", len(meth))
    return meth


def get_methodology_rule(meth: pd.DataFrame, segment: str, cohort: int,
                         mob: int, metric: str) -> dict:
    """Find the best-matching methodology rule using specificity scoring."""
    cohort_str = str(int(cohort))
    mask = (
        ((meth["Segment"] == segment) | (meth["Segment"] == "ALL")) &
        ((meth["Cohort"] == cohort_str) | (meth["Cohort"] == "ALL")) &
        ((meth["Metric"] == metric) | (meth["Metric"] == "ALL")) &
        (meth["MOB_Start"] <= mob) &
        (meth["MOB_End"] >= mob)
    )
    matches = meth[mask]
    if matches.empty:
        return {"Approach": "DEFAULT", "Param1": "nan", "Param2": "nan"}

    # Specificity scoring
    scores = pd.Series(0.0, index=matches.index)
    scores += (matches["Segment"] == segment).astype(float) * 8
    scores += (matches["Cohort"] == cohort_str).astype(float) * 4
    scores += (matches["Metric"] == metric).astype(float) * 2
    mob_range = (matches["MOB_End"] - matches["MOB_Start"]).clip(lower=0) + 1
    scores += 1.0 / mob_range
    best = matches.loc[scores.idxmax()]
    return {
        "Approach": best["Approach"],
        "Param1":   best["Param1"],
        "Param2":   best["Param2"],
    }


# ════════════════════════════════════════════════════════════
# 5. RATE CALCULATION FUNCTIONS
# ════════════════════════════════════════════════════════════

def _fn_cohort_avg(curves: pd.DataFrame, segment: str, cohort: int,
                   mob: int, rate_col: str, lookback: int = 6) -> float:
    """Average of last N MOBs (post-MOB threshold)."""
    mask = (
        (curves["Segment"] == segment) &
        (curves["Cohort"] == cohort) &
        (curves["MOB"] > Config.MOB_THRESHOLD) &
        (curves["MOB"] <= mob)
    )
    subset = curves.loc[mask].sort_values("MOB", ascending=False)
    if len(subset) < 1:
        return None
    vals = subset[rate_col].head(lookback)
    return float(vals.mean())


def _fn_cohort_trend(curves: pd.DataFrame, segment: str, cohort: int,
                     mob: int, rate_col: str) -> float:
    """Linear regression extrapolation on post-MOB-threshold data."""
    mask = (
        (curves["Segment"] == segment) &
        (curves["Cohort"] == cohort) &
        (curves["MOB"] > Config.MOB_THRESHOLD) &
        (curves["MOB"] < mob)
    )
    subset = curves.loc[mask].dropna(subset=[rate_col])
    if len(subset) < 2:
        return None
    x = subset["MOB"].values.astype(float)
    y = subset[rate_col].values.astype(float)
    # Simple linear regression
    n = len(x)
    sx, sy = x.sum(), y.sum()
    sxx = (x * x).sum()
    sxy = (x * y).sum()
    denom = n * sxx - sx * sx
    if abs(denom) < 1e-12:
        return float(y.mean())
    b = (n * sxy - sx * sy) / denom
    a = (sy - b * sx) / n
    return float(a + b * mob)


def _fn_donor_cohort(curves: pd.DataFrame, segment: str, donor_cohort: int,
                     mob: int, rate_col: str) -> float:
    """Copy rate from donor cohort at same MOB."""
    mask = (
        (curves["Segment"] == segment) &
        (curves["Cohort"] == donor_cohort) &
        (curves["MOB"] == mob)
    )
    subset = curves.loc[mask]
    if subset.empty:
        # Try nearest MOB
        mask2 = (
            (curves["Segment"] == segment) &
            (curves["Cohort"] == donor_cohort)
        )
        donor_data = curves.loc[mask2]
        if donor_data.empty:
            return None
        closest_idx = (donor_data["MOB"] - mob).abs().idxmin()
        return float(donor_data.loc[closest_idx, rate_col])
    return float(subset[rate_col].iloc[0])


def _fn_seg_median(curves: pd.DataFrame, segment: str, mob: int,
                   rate_col: str) -> float:
    """Median rate across all cohorts in segment at this MOB."""
    mask = (
        (curves["Segment"] == segment) &
        (curves["MOB"] == mob)
    )
    subset = curves.loc[mask]
    if subset.empty:
        # Fallback: nearest MOB
        seg_data = curves[curves["Segment"] == segment]
        if seg_data.empty:
            return None
        nearest_mob = seg_data.loc[(seg_data["MOB"] - mob).abs().idxmin(), "MOB"]
        subset = seg_data[seg_data["MOB"] == nearest_mob]
    return float(subset[rate_col].median())


def calculate_rate(curves: pd.DataFrame, segment: str, cohort: int,
                   mob: int, metric: str, rule: dict) -> tuple:
    """Apply a methodology rule to get a rate value. Returns (rate, tag)."""
    approach = rule["Approach"]
    p1 = rule["Param1"]

    rate_col = f"{metric}_Rate" if metric in Config.FLOW_METRICS else metric

    if approach == "Manual":
        try:
            return float(p1), "Manual"
        except (ValueError, TypeError):
            return 0.0, "Manual_ERR"

    if approach == "Zero":
        return 0.0, "Zero"

    if approach == "CohortAvg":
        try:
            lb = int(float(p1)) if p1 not in ("nan", "", "None", "NaN") and pd.notna(p1) else Config.DEFAULT_LOOKBACK
        except (ValueError, TypeError):
            lb = Config.DEFAULT_LOOKBACK
        val = _fn_cohort_avg(curves, segment, cohort, mob, rate_col, lb)
        if val is not None:
            return val, "CohortAvg"
        # Fallback: try segment median
        val = _fn_seg_median(curves, segment, mob, rate_col)
        return (val if val is not None else 0.0), "CohortAvg→SegMed"

    if approach == "CohortTrend":
        val = _fn_cohort_trend(curves, segment, cohort, mob, rate_col)
        if val is not None:
            return val, "CohortTrend"
        # Fallback to CohortAvg
        val = _fn_cohort_avg(curves, segment, cohort, mob, rate_col, Config.DEFAULT_LOOKBACK)
        return (val if val is not None else 0.0), "CohortTrend→Avg"

    if approach == "DonorCohort":
        try:
            donor = int(float(p1)) if p1 not in ("nan", "", "None", "NaN") and pd.notna(p1) else cohort
        except (ValueError, TypeError):
            donor = cohort
        val = _fn_donor_cohort(curves, segment, donor, mob, rate_col)
        if val is not None:
            return val, f"Donor:{donor}"
        return 0.0, f"Donor_ERR:{donor}"

    if approach == "SegMedian":
        val = _fn_seg_median(curves, segment, mob, rate_col)
        return (val if val is not None else 0.0), "SegMedian"

    if approach == "DEFAULT":
        # No rule in methodology — use CohortAvg(6) as fallback
        val = _fn_cohort_avg(curves, segment, cohort, mob, rate_col, Config.DEFAULT_LOOKBACK)
        if val is not None:
            return val, "Default_CohortAvg"
        val = _fn_seg_median(curves, segment, mob, rate_col)
        return (val if val is not None else 0.0), "Default_SegMed"

    return 0.0, f"Unknown:{approach}"


def apply_rate_cap(rate: float, metric: str, approach_tag: str) -> float:
    """Cap rate to configured bounds (Manual bypasses caps)."""
    if "Manual" in approach_tag:
        return rate
    if metric in Config.RATE_CAPS:
        lo, hi = Config.RATE_CAPS[metric]
        return max(lo, min(hi, rate))
    return rate


# ════════════════════════════════════════════════════════════
# 6. SEED GENERATION
# ════════════════════════════════════════════════════════════

def generate_seed(agg: pd.DataFrame) -> pd.DataFrame:
    """Create forecast seed from last month of actuals."""
    log.info("Generating forecast seed ...")
    max_cm = agg["CalendarMonth"].max()
    last = agg[agg["CalendarMonth"] == max_cm].copy()

    seed = last.groupby(["Segment", "Cohort"], as_index=False).agg({
        "ClosingGBV": "sum",
        "Provision_Balance": "sum",
        "MOB": "max",
    })
    seed.rename(columns={"ClosingGBV": "OpeningGBV"}, inplace=True)
    seed["MOB"] = seed["MOB"] + 1   # next month's MOB
    seed["Prior_Provision"] = -seed["Provision_Balance"]  # flip sign (raw is negative)
    # Actual coverage from last historical month (used as floor for forecast)
    seed["Seed_Coverage"] = np.where(
        seed["OpeningGBV"].abs() > 1,
        seed["Prior_Provision"] / seed["OpeningGBV"],
        0.0
    )
    seed = seed[seed["OpeningGBV"].abs() > 1].copy()  # drop zero-balance combos

    # Forecast start = month after last actuals
    y, m = max_cm.year, max_cm.month
    m += 1
    if m > 12:
        m = 1
        y += 1
    seed["ForecastMonth"] = pd.Timestamp(y, m, monthrange(y, m)[1])

    log.info("  Seed: %d segment×cohort combos, total OpeningGBV = £%.0f",
             len(seed), seed["OpeningGBV"].sum())
    return seed


# ════════════════════════════════════════════════════════════
# 7. FORECAST ENGINE
# ════════════════════════════════════════════════════════════

def run_forecast(seed: pd.DataFrame, curves: pd.DataFrame,
                 meth: pd.DataFrame, max_months: int) -> pd.DataFrame:
    """Run month-by-month forecast loop."""
    log.info("Running %d-month forecast ...", max_months)
    all_rows = []
    current_seed = seed.copy()

    for step in range(max_months):
        if current_seed.empty:
            log.warning("  No active cohorts left at step %d — stopping.", step)
            break

        fm = current_seed["ForecastMonth"].iloc[0]
        fm_month = fm.month
        is_debt_sale_month = fm_month in Config.DEBT_SALE_MONTHS

        if step % 6 == 0:
            log.info("  Step %d/%d: %s | %d combos | GBV=£%.0f",
                     step + 1, max_months, fm.strftime("%Y-%m"),
                     len(current_seed), current_seed["OpeningGBV"].sum())

        next_seeds = []
        for _, row in current_seed.iterrows():
            seg = row["Segment"]
            coh = int(row["Cohort"])
            mob = int(row["MOB"])
            opening = float(row["OpeningGBV"])
            prior_prov = float(row["Prior_Provision"])
            seed_cov = float(row.get("Seed_Coverage", 0.0))

            # ── Look up rates for all flow metrics ──
            rates = {}
            tags = {}
            for metric in Config.FLOW_METRICS:
                rule = get_methodology_rule(meth, seg, coh, mob, metric)
                rate, tag = calculate_rate(curves, seg, coh, mob, metric, rule)
                rate = apply_rate_cap(rate, metric, tag)
                rates[metric] = rate
                tags[metric] = tag

            # ── Look up coverage ratio ──
            rule = get_methodology_rule(meth, seg, coh, mob, "Total_Coverage_Ratio")
            cov_rate, cov_tag = calculate_rate(
                curves, seg, coh, mob, "Total_Coverage_Ratio", rule
            )
            cov_rate = apply_rate_cap(cov_rate, "Total_Coverage_Ratio", cov_tag)

            # Floor: don't let coverage drop below the seed's actual coverage
            # (prevents unrealistic drops when donor cohorts lack early provision data)
            if seed_cov > 0 and cov_rate < seed_cov * 0.8:
                cov_rate = seed_cov
                cov_tag = cov_tag + "→SeedFloor"

            # ── Debt sale ratios ──
            rule_dscr = get_methodology_rule(meth, seg, coh, mob, "Debt_Sale_Coverage_Ratio")
            dscr, _ = calculate_rate(curves, seg, coh, mob, "Debt_Sale_Coverage_Ratio", rule_dscr)
            dscr = apply_rate_cap(dscr, "Debt_Sale_Coverage_Ratio", _)

            rule_dspr = get_methodology_rule(meth, seg, coh, mob, "Debt_Sale_Proceeds_Rate")
            dspr, _ = calculate_rate(curves, seg, coh, mob, "Debt_Sale_Proceeds_Rate", rule_dspr)
            dspr = apply_rate_cap(dspr, "Debt_Sale_Proceeds_Rate", _)

            # ── Calculate amounts ──
            # InterestRevenue is annualised rate → divide by 12
            int_rev = opening * rates["InterestRevenue"] / 12.0
            coll_p  = opening * rates["Coll_Principal"]
            coll_i  = opening * rates["Coll_Interest"]
            contra_p = opening * rates["ContraSettlements_Principal"]
            contra_i = opening * rates["ContraSettlements_Interest"]

            # Debt sale write-offs only in sale months
            if is_debt_sale_month:
                wo_ds = opening * rates["WO_DebtSold"]
            else:
                wo_ds = 0.0

            wo_other = opening * rates["WO_Other"]

            # ── GBV Waterfall ──
            # Collections and contras are negative (reduce GBV), added directly
            # Write-offs are positive (reduce GBV), subtracted
            closing_gbv = (opening + int_rev
                           + coll_p + coll_i
                           + contra_p + contra_i
                           - wo_ds - wo_other)

            # Floor at 0 (can't have negative GBV in practice)
            closing_gbv = max(closing_gbv, 0.0)

            # ── Impairment ──
            total_prov_bal = closing_gbv * cov_rate
            total_prov_mov = total_prov_bal - prior_prov

            if is_debt_sale_month and wo_ds > 0:
                ds_prov_release = dscr * wo_ds      # provision released on sold debt
                ds_proceeds     = dspr * wo_ds      # cash from debt sale
            else:
                ds_prov_release = 0.0
                ds_proceeds     = 0.0

            non_ds_prov_mov = total_prov_mov + ds_prov_release
            gross_imp_ex_ds = non_ds_prov_mov + wo_other
            ds_impact       = wo_ds + ds_prov_release + ds_proceeds
            net_imp         = gross_imp_ex_ds + ds_impact

            closing_nbv = closing_gbv - total_prov_bal

            # ── Record row ──
            all_rows.append({
                "ForecastMonth": fm,
                "Segment": seg,
                "Cohort": coh,
                "MOB": mob,
                "OpeningGBV": opening,
                "InterestRevenue": int_rev,
                "Coll_Principal": coll_p,
                "Coll_Interest": coll_i,
                "ContraSettlements_Principal": contra_p,
                "ContraSettlements_Interest": contra_i,
                "WO_DebtSold": wo_ds,
                "WO_Other": wo_other,
                "ClosingGBV": closing_gbv,
                # Rates (for transparency)
                "InterestRevenue_Rate": rates["InterestRevenue"],
                "Coll_Principal_Rate": rates["Coll_Principal"],
                "Coll_Interest_Rate": rates["Coll_Interest"],
                "WO_DebtSold_Rate": rates["WO_DebtSold"],
                "WO_Other_Rate": rates["WO_Other"],
                "ContraSettlements_Principal_Rate": rates["ContraSettlements_Principal"],
                "ContraSettlements_Interest_Rate": rates["ContraSettlements_Interest"],
                # Impairment
                "Total_Coverage_Ratio": cov_rate,
                "Total_Provision_Balance": total_prov_bal,
                "Total_Provision_Movement": total_prov_mov,
                "Debt_Sale_Coverage_Ratio": dscr if is_debt_sale_month else 0.0,
                "Debt_Sale_Proceeds_Rate": dspr if is_debt_sale_month else 0.0,
                "DS_Provision_Release": ds_prov_release,
                "DS_Proceeds": ds_proceeds,
                "Non_DS_Provision_Movement": non_ds_prov_mov,
                "Gross_Impairment_ExDS": gross_imp_ex_ds,
                "DS_Impact": ds_impact,
                "Net_Impairment": net_imp,
                "ClosingNBV": closing_nbv,
                # Approach tags
                "CovRatio_Tag": cov_tag,
            })

            # ── Next seed ──
            if closing_gbv > 1:
                next_fm = fm + pd.DateOffset(months=1)
                next_fm = pd.Timestamp(next_fm.year, next_fm.month,
                                       monthrange(next_fm.year, next_fm.month)[1])
                next_seeds.append({
                    "Segment": seg,
                    "Cohort": coh,
                    "MOB": mob + 1,
                    "OpeningGBV": closing_gbv,
                    "Prior_Provision": total_prov_bal,
                    "Seed_Coverage": seed_cov,  # carry forward for floor
                    "ForecastMonth": next_fm,
                })

        current_seed = pd.DataFrame(next_seeds)

    forecast = pd.DataFrame(all_rows)
    log.info("Forecast complete: %d rows", len(forecast))
    return forecast


# ════════════════════════════════════════════════════════════
# 8. VALIDATION
# ════════════════════════════════════════════════════════════

def validate_forecast(fc: pd.DataFrame) -> pd.DataFrame:
    """Run GBV waterfall and other validation checks."""
    log.info("Validating forecast ...")
    v = fc.copy()

    # GBV waterfall check
    calc_close = (v["OpeningGBV"] + v["InterestRevenue"]
                  + v["Coll_Principal"] + v["Coll_Interest"]
                  + v["ContraSettlements_Principal"] + v["ContraSettlements_Interest"]
                  - v["WO_DebtSold"] - v["WO_Other"])
    v["GBV_Variance"] = (v["ClosingGBV"] - calc_close).abs()

    # Chain check (closing[t] = opening[t+1])
    # This is implicit since we set opening = prior closing in the loop

    # NaN check
    nan_count = v[["ClosingGBV", "Net_Impairment", "ClosingNBV"]].isna().sum().sum()
    if nan_count > 0:
        log.warning("  Found %d NaN values in key columns!", nan_count)

    max_var = v["GBV_Variance"].max()
    log.info("  Max GBV variance: £%.2f", max_var)
    log.info("  Coverage ratio range: %.4f to %.4f",
             v["Total_Coverage_Ratio"].min(), v["Total_Coverage_Ratio"].max())
    return v


# ════════════════════════════════════════════════════════════
# 9. OUTPUT
# ════════════════════════════════════════════════════════════

def export_results(fc: pd.DataFrame, output_dir: str):
    """Export forecast to Excel workbooks."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    log.info("Exporting results to %s", out)

    # ── Summary (by month × segment) ──
    summary = (fc.groupby(["ForecastMonth", "Segment"], as_index=False)
                 .agg({
                     "OpeningGBV": "sum",
                     "InterestRevenue": "sum",
                     "Coll_Principal": "sum",
                     "Coll_Interest": "sum",
                     "ContraSettlements_Principal": "sum",
                     "ContraSettlements_Interest": "sum",
                     "WO_DebtSold": "sum",
                     "WO_Other": "sum",
                     "ClosingGBV": "sum",
                     "Total_Provision_Balance": "sum",
                     "Total_Provision_Movement": "sum",
                     "DS_Provision_Release": "sum",
                     "DS_Proceeds": "sum",
                     "Non_DS_Provision_Movement": "sum",
                     "Gross_Impairment_ExDS": "sum",
                     "DS_Impact": "sum",
                     "Net_Impairment": "sum",
                     "ClosingNBV": "sum",
                 }))
    summary["Total_Coverage_Ratio"] = np.where(
        summary["ClosingGBV"] > 0,
        summary["Total_Provision_Balance"] / summary["ClosingGBV"],
        0
    )
    summary.sort_values(["ForecastMonth", "Segment"], inplace=True)

    # ── Portfolio total (by month) ──
    portfolio = (fc.groupby("ForecastMonth", as_index=False)
                   .agg({
                       "OpeningGBV": "sum",
                       "InterestRevenue": "sum",
                       "Coll_Principal": "sum",
                       "Coll_Interest": "sum",
                       "ContraSettlements_Principal": "sum",
                       "ContraSettlements_Interest": "sum",
                       "WO_DebtSold": "sum",
                       "WO_Other": "sum",
                       "ClosingGBV": "sum",
                       "Total_Provision_Balance": "sum",
                       "Net_Impairment": "sum",
                       "ClosingNBV": "sum",
                   }))
    portfolio["Total_Coverage_Ratio"] = np.where(
        portfolio["ClosingGBV"] > 0,
        portfolio["Total_Provision_Balance"] / portfolio["ClosingGBV"],
        0
    )

    # ── Write Excel ──
    summary_path = out / "Forecast_Summary.xlsx"
    with pd.ExcelWriter(summary_path, engine="openpyxl") as w:
        summary.to_excel(w, sheet_name="By_Segment", index=False)
        portfolio.to_excel(w, sheet_name="Portfolio_Total", index=False)
    log.info("  Wrote %s", summary_path)

    details_path = out / "Forecast_Details.xlsx"
    fc.to_excel(details_path, sheet_name="All_Cohorts", index=False)
    log.info("  Wrote %s", details_path)

    # ── Impairment analysis ──
    imp_cols = [
        "ForecastMonth", "Segment", "Cohort", "MOB", "ClosingGBV",
        "Total_Coverage_Ratio", "Total_Provision_Balance",
        "Total_Provision_Movement", "WO_DebtSold",
        "Debt_Sale_Coverage_Ratio", "DS_Provision_Release",
        "Debt_Sale_Proceeds_Rate", "DS_Proceeds",
        "Non_DS_Provision_Movement", "Gross_Impairment_ExDS",
        "DS_Impact", "Net_Impairment", "ClosingNBV",
    ]
    imp_path = out / "Impairment_Analysis.xlsx"
    fc[imp_cols].to_excel(imp_path, sheet_name="Detail", index=False)
    log.info("  Wrote %s", imp_path)

    # ── Print portfolio summary ──
    print("\n" + "=" * 80)
    print("PORTFOLIO FORECAST SUMMARY")
    print("=" * 80)
    for _, r in portfolio.iterrows():
        print(f"  {r['ForecastMonth'].strftime('%Y-%m')}  "
              f"GBV=£{r['ClosingGBV']:>14,.0f}  "
              f"Cov={r['Total_Coverage_Ratio']:.2%}  "
              f"NetImp=£{r['Net_Impairment']:>12,.0f}  "
              f"NBV=£{r['ClosingNBV']:>14,.0f}")
    print("=" * 80 + "\n")


# ════════════════════════════════════════════════════════════
# 10. MAIN
# ════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Oakbrook Backbook Forecast v2")
    parser.add_argument("--fact-raw", default="Fact_Raw_New.xlsx",
                        help="Path to raw data Excel file")
    parser.add_argument("--methodology", default="Rate_Methodology.csv",
                        help="Path to rate methodology CSV")
    parser.add_argument("--months", type=int, default=40,
                        help="Number of forecast months (default: 40)")
    parser.add_argument("--output", default="output_new",
                        help="Output directory (default: output_new)")
    args = parser.parse_args()

    # 1. Load & transform
    raw = load_and_transform(args.fact_raw)

    # 2. Aggregate
    agg = aggregate_data(raw)

    # 3. Historical curves
    curves = compute_historical_curves(agg)

    # 4. Methodology
    meth = load_methodology(args.methodology)

    # 5. Seed
    seed = generate_seed(agg)

    # 6. Forecast
    forecast = run_forecast(seed, curves, meth, args.months)

    # 7. Validate
    forecast = validate_forecast(forecast)

    # 8. Export
    export_results(forecast, args.output)

    log.info("Done.")


if __name__ == "__main__":
    main()
