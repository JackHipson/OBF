# BB Model: Actuals to Forecast Transition Analysis

**Date**: 2026-02-10
**File Analyzed**: `/home/user/OBF/Forecast Baseline Outputs v3.6 (new collections & impairment).xlsx`
**Sheets Used**: `1_Actuals_Data`, `6_Combined_View`

---

## Executive Summary

Analysis of the transition from actual data (Sep 2025) to forecast data (Oct 2025) reveals a **MAJOR DISCONTINUITY** in the **Coverage Ratio**, which drops by **1,668 basis points (52.3%)** at the forecast starting point.

This suggests either:
1. A methodology change between actuals and forecast calculations
2. A data quality issue at the transition point
3. An intentional model assumption that needs validation

---

## Critical Findings: Sep 2025 → Oct 2025 Transition

### Coverage Ratio - MAJOR DISCONTINUITY
| Metric | Sep 2025 (Actual) | Oct 2025 (Forecast) | Change | % Change |
|--------|-------------------|---------------------|--------|----------|
| **Coverage Ratio** | **31.89%** | **15.21%** | **-1,668 bps** | **-52.3%** |

**This is the most significant finding and requires immediate investigation.**

### Other Key Metrics

| Metric | Sep 2025 (Actual) | Oct 2025 (Forecast) | Change | % Change |
|--------|-------------------|---------------------|--------|----------|
| **Opening GBV** | £276.74m | £275.98m | -£0.76m | -0.3% |
| **Closing GBV** | £275.98m | £263.36m | -£12.62m | -4.6% |
| **Coll_Principal** | -£12.92m | -£13.34m | -£0.42m | -3.2% |
| **Coll_Interest** | -£6.56m | -£5.21m | +£1.34m | +20.5% |
| **Interest Revenue** | £6.48m | £6.00m | -£0.48m | -7.4% |
| **Provision Balance** | £26.64m | £28.53m | +£1.90m | +7.1% |

---

## Monthly Trend: Jul - Dec 2025

### Actuals Period (Jul - Sep 2025)

| Month | GBV Closing | Collections (Principal) | Interest Revenue | Provision Balance | Coverage Ratio |
|-------|-------------|-------------------------|------------------|-------------------|----------------|
| **Jul 2025** | £268.05m | -£12.79m | £6.36m | £27.46m | 31.73% |
| **Aug 2025** | £275.63m | -£11.86m | £6.53m | £29.44m | 32.23% |
| **Sep 2025** | £275.98m | -£12.92m | £6.48m | £26.64m | 31.89% |

### Forecast Period (Oct - Dec 2025)

| Month | GBV Closing | Collections (Principal) | Interest Revenue | Provision Balance | Coverage Ratio |
|-------|-------------|-------------------------|------------------|-------------------|----------------|
| **Oct 2025** | £263.36m | -£13.34m | £6.00m | £28.53m | **15.21%** |
| **Nov 2025** | £250.90m | -£12.81m | £5.52m | £29.90m | 16.13% |
| **Dec 2025** | £236.79m | -£12.49m | £5.12m | £30.28m | 16.97% |

---

## Observations

### 1. Coverage Ratio Jump (PRIMARY CONCERN)
- **Actuals average**: ~32% in Jul-Sep 2025
- **Forecast average**: ~16% in Oct-Dec 2025
- **Gap**: ~16 percentage points or 1,600 bps

**Possible causes:**
- Different provision calculation methodologies between actuals and forecast
- Change in debt sale assumptions (debt sale provisions are typically higher)
- Exclusion of certain provision categories in forecast
- Model calibration issue at the starting point

**Action needed:**
- Review provision calculation logic in both actuals and forecast models
- Check if debt sale provision is included/excluded differently
- Validate coverage ratio curves used in forecast vs actuals
- Confirm methodology alignment with finance team

### 2. GBV Runoff
- Opening GBV matches perfectly (Sep closing = Oct opening at £275.98m)
- GBV declining at ~4-5% per month in forecast period
- This appears reasonable and consistent

### 3. Collections & Revenue
- Principal collections: Relatively stable around £12-13m/month
- Interest collections: Drop from £6.56m (Sep) to £5.21m (Oct) - 20.5% decrease
- Interest revenue: Steady decline from £6.48m to £6.00m - 7.4% decrease

**Potential issue**: Interest collection drop seems high for a single month. May indicate:
- Change in interest rate assumptions
- Different accrual methodology
- Timing differences in how interest is recognized

### 4. Provision Movement
- Provision balance increases by £1.90m from Sep to Oct
- This increase happens despite coverage ratio falling significantly
- Suggests provisions are growing in absolute terms but not keeping pace with GBV risk profile

---

## Recommended Actions

1. **PRIORITY: Investigate coverage ratio methodology**
   - Compare provision calculation formulas between actuals and forecast
   - Check if debt sale provisions are handled consistently
   - Review provision curves applied in the forecast model

2. **Validate interest collection assumptions**
   - Review why interest collections drop 20.5% from Sep to Oct
   - Confirm interest rate curves are calibrated correctly
   - Check accrual methodology consistency

3. **Reconcile provision movements**
   - Understand why provisions increase while coverage ratio decreases
   - Review Stage 1/2/3 provision allocation in forecast
   - Compare against historical provision trends

4. **Consider smoothing**
   - If methodology change is valid, consider phasing it in over 2-3 months
   - Sharp discontinuities can raise questions in board reporting
   - Document rationale clearly for audit trail

---

## Data Sources

- **Actuals Data**: Sheet `1_Actuals_Data` (Jan 2019 - Sep 2025)
- **Forecast Data**: Sheet `5_Forecast_Output` (Oct 2025 - Dec 2028)
- **Combined View**: Sheet `6_Combined_View` (both actuals and forecast)
- **Summary Output**: Sheet `9_Summary` (aggregated monthly totals)
- **Impairment Detail**: Sheet `11_Impairment` (provision movements by cohort/MOB)

---

## Technical Notes

- Analysis performed using Python pandas
- All segments aggregated together (NON PRIME, NRP-L, NRP-M, NRP-S, PRIME)
- Values shown in millions (£m) and percentages
- Coverage Ratio = Total Provision Balance / Closing GBV

---

## Files Generated

1. `/home/user/OBF/analyze_bb_transition.py` - Initial forecast analysis script
2. `/home/user/OBF/check_date_range.py` - Date range validation script
3. `/home/user/OBF/list_all_sheets.py` - Sheet inventory script
4. `/home/user/OBF/analyze_actuals_to_forecast_transition.py` - Full transition analysis script
5. `/home/user/OBF/BB_Transition_Analysis_Summary.md` - This summary document
