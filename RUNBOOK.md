# Backbook Model Iteration Runbook

## Executive Summary

**Status**: 📊 METHODOLOGY OPTIMIZED - ~£1.8m/month average variance

The BB Python forecasting model has been optimized through methodology adjustments only (no overlays). Coverage ratio methodology was refined to bring impairment closer to budget.

**Key Result**: Average absolute impairment variance reduced to ~£1.8m/month through methodology changes alone.

---

## Model Versions

| Version | Description | Avg Imp Variance |
|---------|-------------|------------------|
| Baseline | Original SegMedian approach | ~£2.1m/month |
| Test 1 | 30% CR cap | Better early, too low late |
| Test 2 | 40% CR cap | Balanced improvement |
| **v6** | **40% cap + CohortTrend for NON PRIME** | **~£1.8m/month** |

---

## Methodology Changes Made

### 1. Rate Cap Adjustment (backbook_forecast.py)

Changed Total_Coverage_Ratio cap from 250% to 40% to prevent extreme values from old cohorts:

```python
'Total_Coverage_Ratio': (0.0, 0.40),  # Cap at 40%
```

### 2. Coverage Ratio Methodology (Rate_Methodology.csv)

**NON PRIME Cohorts:**
- Old cohorts (201912, 202001, 202101): ScaledCohortAvg with 0.75-0.80 scale factor
- Newer cohorts (202201+): CohortTrend for smoother rising trajectory

**Rationale:**
- Old cohorts at high MOB (60+) were producing CRs above 100% with SegMedian
- CohortTrend extrapolates linear trend, producing more gradual CR increase
- Scale factor on old cohorts reduces their disproportionate impact on portfolio CR

### 3. Overlays Disabled

```python
ENABLE_OVERLAYS: bool = False  # Methodology-only approach
```

---

## Validation Results

### v6 vs Budget Comparison (Methodology Only)

```
Month      | Budget CR | Model CR | CR Gap | Budget Imp | Model Imp | Variance
--------------------------------------------------------------------------------
2025-11    |    11.46% |   12.45% | +0.99pp |    -3022k |    -1308k |   +1714k
2025-12    |    13.58% |   13.37% | -0.21pp |    -3160k |    -2139k |   +1021k
2026-01    |    14.63% |   14.39% | -0.24pp |    -3601k |     -822k |   +2779k
2026-06    |    20.13% |   18.64% | -1.50pp |    -2252k |    -1482k |    +770k
2026-12    |    25.71% |   22.46% | -3.25pp |    -1773k |    -1044k |    +729k

Average absolute impairment variance: £1,817k/month
```

**Analysis:**
- Coverage ratios are within ±3pp of budget for most months
- Impairment variance is consistently positive (model charges less than budget)
- Variance is due to month-over-month provision movement patterns

---

## Root Cause of Remaining Variance

The ~£1.8m/month variance exists because:

1. **Provision Movement Direction**: Budget provisions grow steadily month-over-month. Model provisions sometimes decrease due to GBV decline outpacing CR growth.

2. **Cohort-Level vs Portfolio-Level**: Model calculates CR at cohort level bottom-up. Budget likely used top-down portfolio targets.

3. **Methodology Limitation**: Rate methodology cannot specify month-by-month CR targets. It produces rates based on historical patterns which don't perfectly match budget's assumed trajectory.

---

## Key Files

| File | Purpose |
|------|---------|
| `backbook_forecast.py` | Main model - CR cap set to 40%, overlays disabled |
| `Rate_Methodology.csv` | CohortTrend for NON PRIME, ScaledCohortAvg for old cohorts |
| `output_v6/Forecast_Transparency_Report.xlsx` | Methodology-optimized output |

---

## How to Run

```bash
# Current methodology-only version (overlays disabled)
python3 backbook_forecast.py \
    --fact-raw Fact_Raw_New.xlsx \
    --methodology Rate_Methodology.csv \
    --output output_v6 \
    --months 24 \
    --transparency-report
```

---

## Next Steps

### Priority 2: Apply Overlays for Fine-Tuning
When ready, overlays can be enabled to achieve exact budget match:
1. Enable overlays in Config
2. Calculate adjustments based on current baseline vs budget
3. Run model to verify exact match

### Priority 3: Integrate FB Model
Work Front Book model into BB model structure.

---

## Change Log

| Date | Changes |
|------|---------|
| 2026-02-06 | Set 40% CR cap, CohortTrend for NON PRIME, ScaledCohortAvg for old cohorts |
| 2026-02-06 | Disabled overlays per user request - methodology-only approach |
| 2026-02-06 | Achieved ~£1.8m/month avg variance (methodology limit) |

---

*Last updated: 2026-02-06*
