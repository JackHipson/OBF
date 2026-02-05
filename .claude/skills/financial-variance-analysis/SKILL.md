---
name: financial-variance-analysis
description: Analyze variances between budget and actuals for loan portfolios. Use when investigating budget gaps, explaining variance drivers, comparing forecast vs actual performance, or conducting financial reviews.
argument-hint: "[metric] [period]"
---

# Financial Variance Analysis

Analyze financial variances between budget/forecast and actuals for loan portfolio metrics.

## When to Use This Skill

- Investigating why actuals differ from budget
- Explaining variance drivers to stakeholders
- Conducting monthly/quarterly financial reviews
- Identifying root causes of GBV, NBV, or P&L variances

## Key Data Sources

Look for these files in the project:
- `Fact_Raw_New.xlsx` - Actuals data with columns: cohort, calendarmonth, openinggbv, closinggbv, principalcollections, interestcollections, etc.
- `Budget consol file.xlsx` - Budget data
- `BB Forecast Baseline Outputs*.xlsx` - Forecast model outputs

## Investigation Process

### Step 1: Load and Prepare Data

```python
import pandas as pd

# Load actuals
actuals = pd.read_excel('Fact_Raw_New.xlsx')
actuals['Month'] = pd.to_datetime(actuals['calendarmonth'].astype(str), format='%Y%m')

# Load budget/forecast
budget = pd.read_excel('Budget consol file.xlsx', sheet_name='P&L analysis - BB')
```

### Step 2: Calculate Variances

For each metric, calculate:
- **Absolute Variance**: Actual - Budget
- **Percentage Variance**: (Actual - Budget) / Budget × 100
- **Direction**: Favorable (F) or Unfavorable (U)

### Step 3: Segment the Analysis

Break down variances by:
1. **Segment**: NON PRIME, NRP-S, NRP-M, NRP-L, PRIME
2. **Cohort**: YYYYMM format (e.g., 202401, 202509)
3. **MOB (Month-on-Book)**: Age of the cohort
4. **Time Period**: Monthly, quarterly, YTD

### Step 4: Identify Root Causes

Common variance drivers in loan portfolios:
- **Collection Rate Differences**: Actual collection rates vs budgeted rates
- **Contra Settlements**: Top-ups causing early loan closures (not in BB model)
- **Debt Sale Timing**: Quarterly debt sales affecting provision releases
- **Coverage Ratio Changes**: Provision as % of GBV
- **MOB Mix Effects**: Composition of cohorts by age
- **Cohort-Specific Anomalies**: Individual cohorts with unusual rates

### Step 5: Quantify Impact

For each driver identified:
```
Impact = Rate Difference × GBV Base
```

Example:
```
Collection rate variance: -1.5pp
GBV base: £276M
Impact: -1.5% × £276M = £4.14M additional collections
```

## Output Format

Present findings in this structure:

```
================================================================================
VARIANCE ANALYSIS: [Metric] - [Period]
================================================================================

SUMMARY:
  Budget:    £XXX.XM
  Actual:    £XXX.XM
  Variance:  £XXX.XM (X.X%)

ROOT CAUSE BREAKDOWN:
  1. [Driver 1]:     £X.XM (XX% of variance)
  2. [Driver 2]:     £X.XM (XX% of variance)
  3. [Other]:        £X.XM (XX% of variance)

DETAILED ANALYSIS:
[Segment-by-segment or cohort-by-cohort breakdown]

RECOMMENDATIONS:
- [Action items for future monitoring]
```

## Key Formulas

### GBV Variance
```
ClosingGBV = OpeningGBV
           + Coll_Principal (negative)
           + Coll_Interest (negative)
           + ContraSettlements_Principal (negative, often £0 in model)
           + ContraSettlements_Interest (negative, often £0 in model)
           + NewLoanAmount (positive, often £0 in BB model)
           + InterestRevenue (positive)
           + WO_DebtSold (negative)
           + WO_Other (negative)
```

### NBV Variance
```
NBV = GBV - Provision
Coverage Ratio = Provision / GBV
```

### Collection Rate
```
Collection Rate = (Coll_Principal + Coll_Interest) / OpeningGBV
```

## Tips

- Always check if comparing like-for-like (BB only vs BB only, or Total vs Total)
- Remember BB models don't include contra settlements or new loans by design
- Debt sales happen quarterly - check timing effects
- MOB 0 often has anomalous rates for new cohorts
