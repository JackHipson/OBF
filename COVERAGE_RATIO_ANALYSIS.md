# Coverage Ratio Deep Dive Analysis

## Executive Summary

This document presents a comprehensive analysis of the coverage ratio forecasting methodology and its impact on the impairment variance vs budget.

**Key Finding:** The current coverage ratio methodology is fundamentally misaligned with the budget trajectory. Specific issues identified:
1. **Manual=0 rules** suppress coverage ratios to zero for 6 cohorts
2. **CohortAvg approach** produces flat projections (not rising as budget expects)
3. **DonorCohort approach** inherits slow-rising curves from donors

**Recommended Solution:** Switch to CohortTrend approach with targeted fixes.

**Confidence Level:** 0.90

---

## 1. Budget vs Model: The Gap

### Budget Coverage Ratio Trajectory
```
Nov-25: 11.5% → Dec-26: 26%
Increase: +14.5pp over 14 months
Rate: +1.04pp/month
```

### Python Model v3.5 Coverage Ratio Trajectory
```
Nov-25: 10.6% → Dec-26: 16%
Increase: +5.4pp over 14 months
Rate: +0.39pp/month
```

### Gap
The model produces coverage ratios that rise ~2.7x slower than budget expects.

---

## 2. Root Causes Identified

### Issue 1: Manual=0 Rules (CRITICAL)
Six cohorts have coverage ratios forced to zero:

| Segment | Cohort | GBV Share | Actual CR | Methodology | Impact |
|---------|--------|-----------|-----------|-------------|--------|
| NRP-M | 202301 | 4.3% | 11.8% | Manual=0 | Massive |
| NRP-M | 202001 | <1% | ~0% | Manual=0 | Low |
| NRP-M | 202101 | <1% | ~0% | Manual=0 | Low |
| NRP-S | 202001 | <1% | ~0% | Manual=0 | Low |
| NRP-S | 202101 | <1% | ~0% | Manual=0 | Low |
| PRIME | 202101 | <1% | ~0% | Manual=0 | Low |

**NRP-M 202301 is critical** - 4.3% of GBV, actual CR of 11.8%, but being forced to 0%.

### Issue 2: CohortAvg Produces Flat Projections
CohortAvg averages the last N MOBs and projects forward. This does NOT capture rising trends.

Used for: NON PRIME 201912, 202001, 202101, and various NRP-L/PRIME cohorts.

Example: NON PRIME 201912
- Last 6 MOBs average: ~100% CR
- Projection: Flat at 100%
- But this doesn't help newer cohorts build coverage

### Issue 3: DonorCohort Inherits Slow-Rising Curves
NON PRIME uses DonorCohort extensively, but the donors have slow-rising CR curves:

| Donor | Avg CR Change/Month |
|-------|---------------------|
| 202001 | +0.15pp/month |
| 202101 | +0.10pp/month |
| 202201 | +0.34pp/month |

**Required: +1.04pp/month to match budget**

---

## 3. GBV Concentration Analysis

Top 15 cohort×segment combinations = 50.6% of total GBV.

| Rank | Segment | Cohort | GBV Share | Current Methodology | Issue |
|------|---------|--------|-----------|---------------------|-------|
| 1 | NON PRIME | 202507 | 4.9% | DonorCohort | Slow donor |
| 2 | NRP-M | 202301 | 4.3% | Manual=0 | **WRONG** |
| 3 | NON PRIME | 202509 | 4.2% | DonorCohort | Slow donor |
| 4 | NON PRIME | 202506 | 4.0% | DonorCohort | Slow donor |
| 5 | NON PRIME | 202508 | 3.8% | DonorCohort | Slow donor |
| 6 | NON PRIME | 202505 | 3.6% | DonorCohort | Slow donor |
| 7 | NON PRIME | 202504 | 3.4% | DonorCohort | Slow donor |
| 8 | NRP-M | 202509 | 3.2% | CohortTrend | OK |
| 9 | NRP-M | 202507 | 3.1% | CohortTrend | OK |
| 10 | NRP-M | 202504 | 2.8% | CohortTrend | OK |

---

## 4. Historical Coverage Ratio Patterns

### By MOB (Natural Trajectory)
Coverage ratios DO rise naturally with MOB:

| MOB Range | NON PRIME | NRP-S | NRP-M | NRP-L | PRIME |
|-----------|-----------|-------|-------|-------|-------|
| 5-9 | 17.9% | 5.9% | 5.3% | 6.0% | 2.2% |
| 15-19 | 38.5% | 15.0% | 14.6% | 15.6% | 10.1% |
| 25-29 | 49.1% | 16.7% | 16.6% | - | 13.0% |
| 35-39 | 97.7% | 20.8% | 18.7% | - | 12.3% |
| 45-49 | 100.0% | 21.6% | 28.9% | - | 18.8% |

**Key Insight:** Coverage ratios rise naturally by ~1-2pp/MOB for most segments.

### Individual Cohort Trends
Cohorts showing fast CR rises (≥1.04pp/month):
- NON PRIME: 201912, 202404-202410 (newer cohorts)
- NRP-S: 201912
- NRP-M: 202410
- NRP-L: 202405

Most cohorts show slower rises (avg 0.31pp/month).

---

## 5. Approach Comparison

### CohortAvg
- **Mechanics:** Average of last N MOBs
- **Produces:** Flat projection at recent average
- **Budget Fit:** ❌ Does not capture rising trend
- **Use Case:** Stable, mature cohorts where CR has plateaued

### CohortTrend
- **Mechanics:** Linear regression extrapolation
- **Produces:** Rising/falling projection following trend
- **Budget Fit:** ✅ Can capture rising trend
- **Simulated Output:** +6m: 23%, +12m: 32% (close to/exceeds budget)
- **Use Case:** Cohorts with clear trend in data

### DonorCohort
- **Mechanics:** Copy rates from specified donor
- **Produces:** Depends on donor's curve
- **Budget Fit:** ⚠️ Only if donor has steep rise
- **Current Issue:** Donors have slow-rising curves
- **Use Case:** New cohorts with insufficient data

### SegMedian
- **Mechanics:** Median across segment at each MOB
- **Produces:** Segment-level pattern
- **Budget Fit:** ⚠️ Captures segment rise, loses cohort variation
- **Use Case:** Fallback when cohort data insufficient

### Manual
- **Mechanics:** Fixed rate
- **Produces:** Whatever you specify
- **Budget Fit:** ✅ Can match exactly
- **Use Case:** Final calibration or known overrides

---

## 6. Recommended Strategy

### Phase 1: Quick Wins (Immediate)
1. **Remove Manual=0 for NRP-M 202301** → Replace with CohortTrend
   - Impact: +0.5pp on total CR (this alone is significant)

2. **Remove other Manual=0 rules** where actual CR > 0
   - NRP-S 202001, 202101
   - Replace with CohortAvg (these have minimal GBV)

### Phase 2: NON PRIME Methodology Change
1. **Switch from DonorCohort to CohortTrend** for newer NON PRIME cohorts
   - Affects: 202404-202509 (combined ~26% of GBV)
   - Expected impact: CR rises faster as CohortTrend extrapolates their own rising patterns

2. **Keep CohortAvg for mature cohorts** (201912, 202001, 202101)
   - These have high CR already (~100%) and are running off

### Phase 3: Validate & Calibrate
1. Re-run model with new methodology
2. Compare to budget CR trajectory
3. If needed, apply Manual overrides for fine-tuning

### Phase 4: Fine-Tuning (if needed)
If Phase 2 overshoots budget:
- Use rate caps to limit CR rise
- Apply segment-level scaling factors

If Phase 2 undershoots budget:
- Consider SegMedian as additional boost
- Apply manual overlays

---

## 7. Expected Impact

### Before (Current v3.5)
- Total CR at Dec-26: ~16%
- Impairment variance: +£2-3m/month (less than budget)

### After (Recommended Changes)
- Total CR at Dec-26: ~26-32% (simulation suggests ~32%)
- Impairment variance: Should align with budget (may need caps if overshoots)

### Risk Assessment
- **Risk of overshoot:** Medium - CohortTrend simulation shows 32% at +12m
- **Mitigation:** Apply CR caps at segment level if needed
- **Downside:** If we overshoot, impairment will be HIGHER than budget (easier to cap down than push up)

---

## 8. Specific Methodology Changes

### Changes to Rate_Methodology.csv

```csv
# REMOVE these rules:
NRP-M,202301,Total_Coverage_Ratio,0,999,Manual,0,,
NRP-M,202001,Total_Coverage_Ratio,0,999,Manual,0,,
NRP-M,202101,Total_Coverage_Ratio,0,999,Manual,0,,
NRP-S,202001,Total_Coverage_Ratio,0,999,Manual,0,,
NRP-S,202101,Total_Coverage_Ratio,0,999,Manual,0,,
PRIME,202101,Total_Coverage_Ratio,0,999,Manual,0,,

# ADD these replacement rules:
NRP-M,202301,Total_Coverage_Ratio,0,999,CohortTrend,,,CR should rise with trend
NRP-M,202001,Total_Coverage_Ratio,0,999,CohortAvg,6,,minimal balance
NRP-M,202101,Total_Coverage_Ratio,0,999,CohortAvg,6,,minimal balance
NRP-S,202001,Total_Coverage_Ratio,0,999,CohortAvg,6,,minimal balance
NRP-S,202101,Total_Coverage_Ratio,0,999,CohortAvg,6,,minimal balance
PRIME,202101,Total_Coverage_Ratio,0,999,CohortAvg,6,,minimal balance

# CHANGE these rules (NON PRIME from DonorCohort to CohortTrend):
NON PRIME,202404,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202405,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202406,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202407,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202408,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202409,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202410,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202411,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202412,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202501,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202502,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202503,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202504,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202505,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202506,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202507,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202508,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
NON PRIME,202509,Total_Coverage_Ratio,0,999,CohortTrend,,,switch from DonorCohort
```

---

## 9. Next Steps

1. **Confirm alignment** on this analysis and recommended approach
2. **Implement Phase 1** (remove Manual=0) and test
3. **Implement Phase 2** (switch NON PRIME to CohortTrend) and test
4. **Validate output** against budget CR trajectory
5. **Apply caps/overlays** if needed for final calibration

---

*Analysis completed: 2026-02-06*
*Analyst: Claude Code*
*Confidence: 0.90*
