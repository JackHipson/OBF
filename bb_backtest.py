"""
bb_backtest.py - Backtesting Framework for Backbook Forecast
=============================================================
Re-runs the forecast from historical cutoff dates and compares
predicted values against actual outcomes.

Usage:
    python bb_backtest.py [--cutoff 202503] [--months 6] [--output backtest_output]
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import argparse

# Import forecast machinery from bb_forecast_new
from bb_forecast_new import (
    Config, load_and_transform, aggregate_data, compute_historical_curves,
    load_methodology, run_forecast, _ym_to_date
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def generate_backtest_seed(agg: pd.DataFrame, cutoff_ym: int) -> pd.DataFrame:
    """Generate seed from a specific historical cutoff month."""
    from calendar import monthrange

    cutoff_date = _ym_to_date(cutoff_ym)
    last = agg[agg["CalendarMonth"] == cutoff_date].copy()

    if last.empty:
        raise ValueError(f"No data at cutoff month {cutoff_ym} ({cutoff_date})")

    seed = last.groupby(["Segment", "Cohort"], as_index=False).agg({
        "ClosingGBV": "sum",
        "Provision_Balance": "sum",
        "MOB": "max",
    })
    seed.rename(columns={"ClosingGBV": "OpeningGBV"}, inplace=True)
    seed["MOB"] = seed["MOB"] + 1
    seed["Prior_Provision"] = -seed["Provision_Balance"]
    seed["Seed_Coverage"] = np.where(
        seed["OpeningGBV"].abs() > 1,
        seed["Prior_Provision"] / seed["OpeningGBV"],
        0.0
    )
    seed = seed[seed["OpeningGBV"].abs() > 1].copy()

    y, m = divmod(cutoff_ym, 100)
    m += 1
    if m > 12:
        m = 1
        y += 1
    seed["ForecastMonth"] = pd.Timestamp(y, m, monthrange(y, m)[1])

    log.info("  Backtest seed at %d: %d combos, GBV=£%.0f",
             cutoff_ym, len(seed), seed["OpeningGBV"].sum())
    return seed


def get_actuals_for_comparison(agg: pd.DataFrame, start_ym: int, months: int,
                               backbook_cohorts: set = None) -> pd.DataFrame:
    """Extract actual data for the forecast period to compare against.
    If backbook_cohorts is given, only include those cohorts (backbook-only comparison)."""
    start_date = _ym_to_date(start_ym)
    actuals = agg[agg["CalendarMonth"] >= start_date].copy()

    if backbook_cohorts:
        actuals = actuals[actuals["Cohort"].isin(backbook_cohorts)].copy()

    # Aggregate to Segment × CalendarMonth for comparison
    act_summary = (actuals.groupby(["CalendarMonth", "Segment"], as_index=False)
                          .agg({
                              "OpeningGBV": "sum",
                              "ClosingGBV": "sum",
                              "InterestRevenue": "sum",
                              "Coll_Principal": "sum",
                              "Coll_Interest": "sum",
                              "WO_DebtSold": "sum",
                              "WO_Other": "sum",
                              "ContraSettlements_Principal": "sum",
                              "ContraSettlements_Interest": "sum",
                              "Provision_Balance": "sum",
                          }))
    act_summary["Total_Coverage_Ratio"] = np.where(
        act_summary["ClosingGBV"].abs() > 1,
        -act_summary["Provision_Balance"] / act_summary["ClosingGBV"],
        0.0
    )
    act_summary.rename(columns={"CalendarMonth": "ForecastMonth"}, inplace=True)
    return act_summary


def compute_variance(forecast_summary: pd.DataFrame,
                     actuals_summary: pd.DataFrame) -> pd.DataFrame:
    """Compare forecast vs actuals and compute variances."""
    # Aggregate forecast to same level
    fc_agg = (forecast_summary.groupby(["ForecastMonth", "Segment"], as_index=False)
                              .agg({
                                  "OpeningGBV": "sum",
                                  "ClosingGBV": "sum",
                                  "InterestRevenue": "sum",
                                  "Coll_Principal": "sum",
                                  "Coll_Interest": "sum",
                                  "WO_DebtSold": "sum",
                                  "WO_Other": "sum",
                                  "ContraSettlements_Principal": "sum",
                                  "ContraSettlements_Interest": "sum",
                                  "Total_Provision_Balance": "sum",
                              }))
    fc_agg["Total_Coverage_Ratio"] = np.where(
        fc_agg["ClosingGBV"].abs() > 1,
        fc_agg["Total_Provision_Balance"] / fc_agg["ClosingGBV"],
        0.0
    )

    # Merge
    merged = pd.merge(
        fc_agg, actuals_summary,
        on=["ForecastMonth", "Segment"],
        suffixes=("_FC", "_ACT"),
        how="inner"
    )

    # Compute variances
    for metric in ["OpeningGBV", "ClosingGBV", "InterestRevenue",
                   "Coll_Principal", "Coll_Interest", "WO_DebtSold"]:
        fc_col = f"{metric}_FC"
        act_col = f"{metric}_ACT"
        if fc_col in merged.columns and act_col in merged.columns:
            merged[f"{metric}_Var"] = merged[fc_col] - merged[act_col]
            merged[f"{metric}_Var%"] = np.where(
                merged[act_col].abs() > 1,
                (merged[fc_col] - merged[act_col]) / merged[act_col].abs() * 100,
                0.0
            )

    # Coverage variance
    merged["Coverage_Var_pp"] = (merged["Total_Coverage_Ratio_FC"]
                                  - merged["Total_Coverage_Ratio_ACT"]) * 100  # ppt

    return merged


def run_backtest(fact_raw_path: str, meth_path: str, cutoff_ym: int,
                 months: int, output_dir: str):
    """Run a complete backtest from a historical cutoff."""
    log.info("=" * 60)
    log.info("BACKTEST: Cutoff=%d, Months=%d", cutoff_ym, months)
    log.info("=" * 60)

    # Load full data
    raw = load_and_transform(fact_raw_path)
    agg_full = aggregate_data(raw)

    # Restrict curves to data up to cutoff (simulates not having future info)
    cutoff_date = _ym_to_date(cutoff_ym)
    agg_cutoff = agg_full[agg_full["CalendarMonth"] <= cutoff_date].copy()
    curves = compute_historical_curves(agg_cutoff)
    meth = load_methodology(meth_path)

    # Seed from cutoff
    seed = generate_backtest_seed(agg_cutoff, cutoff_ym)

    # Run forecast
    forecast = run_forecast(seed, curves, meth, months)

    # Get actuals for comparison
    y, m = divmod(cutoff_ym, 100)
    m += 1
    if m > 12:
        m = 1
        y += 1
    start_ym = y * 100 + m
    # Only compare against cohorts that existed at cutoff (backbook only)
    backbook_cohorts = set(seed["Cohort"].unique())
    actuals = get_actuals_for_comparison(agg_full, start_ym, months, backbook_cohorts)

    # Compute variance
    variance = compute_variance(forecast, actuals)

    # Export
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(out / f"Backtest_{cutoff_ym}.xlsx", engine="openpyxl") as w:
        # Forecast summary
        fc_summary = (forecast.groupby(["ForecastMonth", "Segment"], as_index=False)
                              .agg({c: "sum" for c in [
                                  "OpeningGBV", "ClosingGBV", "InterestRevenue",
                                  "Coll_Principal", "Coll_Interest", "WO_DebtSold", "WO_Other",
                                  "Total_Provision_Balance", "Net_Impairment", "ClosingNBV",
                              ]}))
        fc_summary.to_excel(w, sheet_name="Forecast", index=False)
        actuals.to_excel(w, sheet_name="Actuals", index=False)
        variance.to_excel(w, sheet_name="Variance", index=False)

        # Portfolio-level variance summary
        port_var = (variance.groupby("ForecastMonth", as_index=False)
                            .agg({
                                "ClosingGBV_FC": "sum",
                                "ClosingGBV_ACT": "sum",
                                "InterestRevenue_FC": "sum",
                                "InterestRevenue_ACT": "sum",
                                "Coll_Principal_FC": "sum",
                                "Coll_Principal_ACT": "sum",
                            }))
        port_var["GBV_Var%"] = (port_var["ClosingGBV_FC"] - port_var["ClosingGBV_ACT"]) / port_var["ClosingGBV_ACT"].abs() * 100
        port_var.to_excel(w, sheet_name="Portfolio_Variance", index=False)

    log.info("Backtest output: %s", out / f"Backtest_{cutoff_ym}.xlsx")

    # Print summary
    print(f"\n{'='*70}")
    print(f"BACKTEST RESULTS: Cutoff {cutoff_ym}")
    print(f"{'='*70}")
    for _, r in port_var.iterrows():
        fm = r["ForecastMonth"]
        if isinstance(fm, str):
            fm_str = fm[:7]
        else:
            fm_str = fm.strftime("%Y-%m")
        print(f"  {fm_str}  "
              f"FC_GBV=£{r['ClosingGBV_FC']:>12,.0f}  "
              f"ACT_GBV=£{r['ClosingGBV_ACT']:>12,.0f}  "
              f"Var={r['GBV_Var%']:+.1f}%")
    print(f"{'='*70}\n")

    return forecast, actuals, variance


def main():
    parser = argparse.ArgumentParser(description="Backtest Backbook Forecast")
    parser.add_argument("--fact-raw", default="Fact_Raw_New.xlsx")
    parser.add_argument("--methodology", default="Rate_Methodology.csv")
    parser.add_argument("--cutoff", type=int, default=202503,
                        help="Cutoff month YYYYMM (default: 202503)")
    parser.add_argument("--months", type=int, default=6,
                        help="Months to forecast from cutoff (default: 6)")
    parser.add_argument("--output", default="backtest_output")
    args = parser.parse_args()

    run_backtest(args.fact_raw, args.methodology, args.cutoff,
                 args.months, args.output)


if __name__ == "__main__":
    main()
