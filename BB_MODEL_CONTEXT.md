# BB Model Context & Status Document

## Executive Summary

This document captures the complete context for the Backbook (BB) Python forecasting model as of 2026-02-06. The model forecasts loan portfolio performance (GBV, NBV, collections, revenue, impairment) for 12-36 months.

**Current State:** Model produces sensible outputs for Collections and Interest Revenue. **Gross Impairment is the priority** - there is a significant variance vs budget that needs to be resolved.

**Confidence Level:** 0.85 - High confidence in diagnosis (coverage ratio variance), medium confidence on optimal solution approach.

---

## 1. Prior Context Summary

### 1.1 Previous Work Completed
1. **V39 Budget Model** - Initial Python implementation
2. **Scenario Forecasting** - At cohort × segment level
3. **MOB 0 Anomaly Fix** - Fixed 202509 cohort rate extrapolation issue
4. **NBV Analysis** - Investigated NBV vs budget discrepancy
5. **Contra Settlements Discovery** - Found ~£35M/year not modeled (by design for BB runoff model)
6. **Claude Code Skills** - Created 8 financial analysis skills

### 1.2 Model Understanding
The model is a **BB runoff model** - it forecasts the rundown of existing back-book loans without new originations. Key design decisions:
- ContraSettlements = £0 (by design - old loans stay on BB, top-up increments go to FB)
- NewLoanAmount = £0 (by design - no new originations in BB)
- This is correct for a standalone BB model; FB model handles new business

---

## 2. Current State

### 2.1 Model Version
- **Version:** v3.5 (Forecast Baseline Outputs v3.5 (new collections).xlsx)
- **Branch:** `BB-Model-Final-Build`
- **Key Files:**
  - `backbook_forecast.py` - Main Python model
  - `Rate_Methodology.csv` - Control table
  - `Fact_Raw_New.xlsx` - Input data

### 2.2 Metric-by-Metric Status

| Metric | Status | Variance vs Budget | Notes |
|--------|--------|-------------------|-------|
| **Collections** | DONE | +£1.7m early, converging later | Acceptable |
| **Interest Revenue** | DONE | -£0.4m to -£0.9m | Minor, acceptable |
| **Gross Impairment** | **PRIORITY** | +£1m to +£3m/month | Python shows LESS impairment than budget |
| Closing GBV | Derived | -£4m to -£39m | Will improve when impairment fixed |
| Closing NBV | Derived | -£1.5m to -£22m | Will improve when impairment fixed |

### 2.3 Key Variance Numbers (Sample Months)

```
Month       GBV Var      NBV Var      Gross Imp Var
-----------------------------------------------
Nov-25      -£4.1m       -£1.5m       +£2.1m (less impairment)
Jan-26      -£18.7m      -£10.5m      +£3.0m
Jun-26      -£32.5m      -£17.8m      +£1.3m
Dec-26      -£43.9m      -£20.9m      +£1.9m
```

---

## 3. Root Cause Analysis: Impairment Variance

### 3.1 The Problem
Budget expects monthly gross impairment of ~£2-3.6m (negative = charge).
Python model produces ~£0.5m to -£1m (much lower charges, sometimes releases).

### 3.2 Root Cause: Coverage Ratio Trajectory
Impairment is driven by **coverage ratio** (Provision ÷ GBV):

```
COVERAGE RATIO COMPARISON:

Month       Python CR    Budget CR    Gap
----------------------------------------
Nov-25      10.61%       11.46%       -0.85pp
Jan-26      12.23%       14.63%       -2.40pp
Jun-26      15.30%       20.13%       -4.83pp
Sep-26      15.80%       21.48%       -5.68pp
Dec-26      16.19%       25.71%       -9.52pp
```

**Key Insight:**
- Budget assumes coverage ratios rise from ~11.5% to ~26% (+14.5pp)
- Python model only rises from ~10.6% to ~16% (+5.4pp)
- Gap grows to ~10pp by end of forecast

### 3.3 Why This Matters
```
Impairment = Change in Provision Balance + Write-offs
Provision Balance = Coverage Ratio × GBV

If Coverage Ratio rises slowly → Provision builds slowly
If GBV falls fast (as expected in runoff) → Provision might DECLINE
Declining provision = Provision RELEASE = Lower/negative impairment
```

The Python model's coverage ratios don't rise fast enough to offset the GBV decline, resulting in lower impairment charges.

### 3.4 Current Rate Methodology for Coverage Ratios
The Rate_Methodology.csv uses:
- **CohortAvg** - Averages last 6 MOBs (for mature cohorts)
- **DonorCohort** - Copies rates from older cohorts (for newer cohorts)
- **CohortTrend** - Linear extrapolation (for some NRP segments)
- **Manual** - Fixed values (for negligible balance cohorts)

**Problem:** These approaches extrapolate historical patterns, which don't show coverage ratios rising as fast as budget assumes.

---

## 4. Outstanding To-Do List

### Priority 1: Fix Impairment (Coverage Ratios)
- [ ] **Investigate budget's coverage methodology** - How did budget calculate/assume coverage ratios?
- [ ] **Test Manual coverage ratio overrides** - Match budget's implied coverage trajectory
- [ ] **Update Rate_Methodology.csv** - Implement segment-level coverage ratio curves
- [ ] **Re-run model and validate** - Impairment should align with budget

### Priority 2: Final Calibration
- [ ] Fine-tune any remaining variances with overlays
- [ ] Document all methodology choices
- [ ] Verify GBV/NBV cascade correctly after impairment fix

### Priority 3: FB-BB Integration
- [ ] Work existing FB model into BB model
- [ ] Create combined FB-BB model (5 FB modules + BB)
- [ ] Validate total book reconciliation

---

## 5. Approach for Fixing Impairment

### Recommended Iteration Strategy

**Step 1: Understand the Target**
- Extract budget's monthly coverage ratios by segment
- Understand any segment-level patterns

**Step 2: Test Manual Override Approach**
```csv
# Example Rate_Methodology additions:
ALL,ALL,Total_Coverage_Ratio,0,999,Manual,0.12,,Nov-25 starting point
ALL,ALL,Total_Coverage_Ratio,0,999,Manual,0.26,,Dec-26 ending point
```
This would force coverage ratios to match budget, but loses cohort-level granularity.

**Step 3: Iterate with ScaledCohortAvg or Multipliers**
If budget uses a multiplier or scaling factor on top of historical patterns, we can:
- Apply overlay multipliers to coverage ratios
- Scale CohortAvg/CohortTrend outputs by a growth factor

**Step 4: Validate & Document**
- Run model, check impairment variance
- Document final methodology choices
- Create reproducible configuration

---

## 6. Key Questions to Resolve

1. **What methodology did the original budget model use for coverage ratios?**
   - Was it a portfolio-level curve?
   - Was it segment-specific?
   - Were there manual management overlays?

2. **Is the steep coverage ratio increase in budget driven by:**
   - Expected credit deterioration?
   - Accounting policy (IFRS 9 stage migration)?
   - Debt sale timing assumptions?

3. **Should the Python model use a different approach entirely?**
   - Manual curves matching budget?
   - Scaling factors applied to historical patterns?

---

## 7. Repository Structure

```
/home/user/OBF/
├── backbook_forecast.py          # Main Python model
├── forecast_calibrator.py        # Calibration utilities
├── generate_transparency_report.py
├── Rate_Methodology.csv          # Control table (KEY FILE)
├── Fact_Raw_New.xlsx             # Input data
├── Budget consol file.xlsx       # TARGET (budget outputs)
├── Forecast Baseline Outputs v3.5 (new collections).xlsx  # Current output
├── RUNBOOK.md                    # Change tracking & decisions
├── BB_MODEL_CONTEXT.md           # This document
├── 01_SYSTEM_DESIGN (1).md       # Architecture documentation
├── 02_IMPLEMENTATION_GUIDE (1).md
├── 03_EXAMPLE_OUTPUTS (1).md
└── 04_QUICK_REFERENCE (1).md
```

---

## 8. Success Criteria

The model is "done" when:

1. **Gross Impairment variance < £0.5m/month** vs budget
2. **NBV variance < £5m** vs budget (cumulative effect of impairment fix)
3. **All methodology choices documented** in Rate_Methodology.csv
4. **Reproducible** - Anyone can re-run and get same results

---

## 9. Appendix: Technical Reference

### Impairment Calculation Formula
```python
# Monthly impairment calculation
Provision_Balance[t] = Coverage_Ratio[t] × ClosingGBV[t]
Provision_Movement[t] = Provision_Balance[t] - Provision_Balance[t-1]

# For debt sale months:
Debt_Sale_Provision_Release = DS_Coverage_Ratio × DS_WriteOffs
Debt_Sale_Proceeds = DS_Proceeds_Rate × DS_WriteOffs
Debt_Sale_Impact = DS_WriteOffs + DS_Provision_Release + DS_Proceeds

# Final impairment
Non_DS_Provision_Movement = Provision_Movement + DS_Provision_Release
Gross_Impairment_ExcludingDS = Non_DS_Provision_Movement + WO_Other
Net_Impairment = Gross_Impairment_ExcludingDS + Debt_Sale_Impact
```

### Rate Methodology Options
| Approach | Description | When to Use |
|----------|-------------|-------------|
| CohortAvg | Average of last N MOBs | Stable, mature cohorts |
| CohortTrend | Linear extrapolation | Trending patterns |
| DonorCohort | Copy from older cohort | New cohorts with no history |
| SegMedian | Median across segment | Portfolio-level assumptions |
| Manual | Fixed value | Override specific behavior |
| Zero | Force to zero | Negligible balances |

---

*Document generated: 2026-02-06*
*Model Version: v3.5*
*Branch: BB-Model-Final-Build*
