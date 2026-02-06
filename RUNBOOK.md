# BB Model Final Build - Runbook

## Purpose
This runbook tracks the iteration and finalization of the Python Backbook (BB) forecasting model. It serves as a living document capturing decisions, changes, variances, and progress.

---

## Current Status: IN PROGRESS
**Last Updated:** 2026-02-06
**Current Model Version:** v3.5
**Branch:** `BB-Model-Final-Build`

---

## Quick Reference

### Key Files
| File | Purpose |
|------|---------|
| `backbook_forecast.py` | Main Python forecasting model |
| `Rate_Methodology.csv` | Control table for rate selection by Segment/Cohort/MOB |
| `Fact_Raw_New.xlsx` | Input: Historical loan data |
| `Budget consol file.xlsx` | Target: Budget outputs we're matching to |
| `Forecast Baseline Outputs v3.5 (new collections).xlsx` | Current model output |

### Metric Status
| Metric | Status | Notes |
|--------|--------|-------|
| Collections | DONE | Matching budget reasonably well |
| Interest Revenue | DONE | Matching budget reasonably well |
| **Gross Impairment** | **PRIORITY** | Major variance - coverage ratios too flat |
| Closing GBV | DERIVED | Will fix when impairment fixed |
| Closing NBV | DERIVED | Will fix when impairment fixed |

---

## Change Log

### 2026-02-06: Initial Analysis
**Analyst:** Claude Code

**Findings:**
1. **Coverage Ratio Variance Identified** - Root cause of impairment mismatch
   - Python model: Coverage rises from ~10.6% to ~16% (Δ +5.6pp)
   - Budget: Coverage rises from ~11.5% to ~26% (Δ +14.5pp)
   - Gap: Python under-provisions by ~10pp by end of forecast

2. **Impact on Impairment:**
   - Budget expects Gross Impairment: ~£2-3.6m/month
   - Python produces: ~£0.5m to -£1m/month (much lower)
   - Variance: +£2-3m/month (Python shows less impairment)

3. **Root Cause Analysis:**
   - Current methodology uses CohortAvg, DonorCohort, CohortTrend
   - These approaches extrapolate historical patterns
   - Budget assumes faster coverage ratio increase than historical trends show

**Actions Required:**
- [ ] Investigate budget's coverage ratio methodology/assumptions
- [ ] Test alternative approaches (steeper curves, manual overrides)
- [ ] Iterate Rate_Methodology.csv for Total_Coverage_Ratio

---

## Variance Dashboard

### Latest Variance (v3.5 vs Budget)

| Month | GBV Var | NBV Var | Collections Var | Gross Imp Var |
|-------|---------|---------|-----------------|---------------|
| Nov-25 | -£4.1m | -£1.5m | +£1.7m | +£2.1m |
| Dec-25 | -£14.5m | -£7.3m | +£1.7m | +£1.2m |
| Jan-26 | -£18.7m | -£10.5m | +£1.6m | +£3.0m |
| Mar-26 | -£25.5m | -£15.2m | +£1.6m | +£1.3m |
| Jun-26 | -£32.5m | -£17.8m | +£0.9m | +£1.3m |
| Sep-26 | -£38.1m | -£21.7m | -£0.2m | +£1.1m |
| Dec-26 | -£43.9m | -£20.9m | -£0.8m | +£1.9m |

**Legend:**
- Positive variance = Python higher than Budget
- Negative variance = Python lower than Budget

---

## Iteration Strategy

### Phase 1: Understand Budget Methodology
1. Extract how budget calculated coverage ratios
2. Identify segment-level coverage assumptions
3. Document any manual overlays or adjustments used

### Phase 2: Calibrate Coverage Ratios
1. Test Manual override approach for Total_Coverage_Ratio
2. Create segment-level coverage ratio curves matching budget
3. Validate impairment outputs align

### Phase 3: Fine-Tune & Validate
1. Check all segments individually
2. Verify GBV/NBV cascades correctly
3. Document final methodology choices

### Phase 4: Overlay Implementation (if needed)
1. Apply final overlays to match exact budget numbers
2. Document overlay rationale
3. Create reproducible overlay file

---

## Model Architecture Notes

### Impairment Calculation Flow
```
Coverage Ratio → Provision Balance → Provision Movement → Impairment

Provision_Balance[t] = Coverage_Ratio[t] × ClosingGBV[t]
Provision_Movement[t] = Provision_Balance[t] - Provision_Balance[t-1]
Gross_Impairment = Provision_Movement + WO_Other (+ Debt Sale adjustments)
```

### Key Insight
Budget coverage ratios imply provisions are building faster than GBV is declining.
Python model's coverage ratios don't rise fast enough → smaller provision building → lower impairment.

---

## Questions to Resolve

1. **What methodology did the budget use for coverage ratios?**
   - Was it cohort-based, segment-based, or portfolio-level?
   - Were there manual adjustments or overlays?

2. **Are there seasonal patterns in coverage ratios?**
   - Does model need seasonal adjustment?

3. **How should debt sale months affect coverage ratios?**
   - Pre-sale provision build-up?
   - Post-sale coverage jump?

---

## References

- System Design Doc: `01_SYSTEM_DESIGN (1).md`
- Implementation Guide: `02_IMPLEMENTATION_GUIDE (1).md`
- Rate Methodology Options: CohortAvg, CohortTrend, DonorCohort, SegMedian, Manual, Zero
