---
name: backbook-forecasting
description: Work with backbook loan portfolio forecasting models. Use when building forecasts, debugging rate curves, fixing cohort anomalies, understanding rate methodologies, or modifying forecast assumptions.
argument-hint: "[task] [cohort/segment]"
---

# Backbook Forecasting

Build and maintain backbook (BB) loan portfolio forecasting models.

## When to Use This Skill

- Building or modifying BB forecast models
- Debugging rate curve anomalies
- Fixing cohort-specific issues (e.g., MOB 0 anomalies)
- Understanding rate methodology choices
- Comparing forecast outputs to actuals

## Model Architecture

### What the BB Model Does
- Forecasts how EXISTING loans run off over time
- Projects collections, revenue, write-offs, and closing GBV
- Does NOT include new disbursals (that's Frontbook)
- Does NOT remove contra settlements (by design - loans stay on BB)

### Key Components

```
BB Forecast = f(Opening GBV, Rate Curves, Methodology Rules)
```

1. **Historical Rates**: Calculated from actuals data by cohort/segment/MOB
2. **Extended Curves**: Historical rates extrapolated to future MOBs
3. **Methodology Rules**: Which approach to use for each cohort/segment/MOB
4. **Forecast Output**: Applied rates × GBV = projected cash flows

## Rate Methodologies

### 1. DonorCohort
Uses rates from an older, similar cohort as a proxy.

```yaml
Approach: DonorCohort:202404
Use when: Young cohorts with limited history
How it works: Borrows the rate curve from cohort 202404
```

**Best for**: Cohorts with < 12 months of history

### 2. CohortTrend
Extrapolates from the cohort's own historical rates.

```yaml
Approach: CohortTrend
Param1: 6 (lookback months)
Use when: Cohorts with sufficient history showing clear trends
How it works: Fits a trend to last N months and extrapolates
```

**Warning**: If historical data has anomalies (e.g., extreme MOB 0 rates), CohortTrend will produce unrealistic projections.

### 3. CohortAvg
Uses the average of recent months for flat projection.

```yaml
Approach: CohortAvg
Param1: 6 (averaging months)
Use when: Mature cohorts with stable rates
How it works: Takes average of last N months and holds flat
```

### 4. SegMedian
Uses the median rate across all cohorts in the segment.

```yaml
Approach: SegMedian
Use when: Portfolio-level assumptions needed
How it works: Takes median rate across segment for given MOB
```

### 5. Manual
Hard-coded rate value.

```yaml
Approach: Manual
Param1: 0.05 (the rate value)
Use when: Overriding model with specific assumptions
```

## Rate Methodology File

The `Rate_Methodology.csv` file controls which approach is used:

```csv
Segment,Cohort,Metric,MOB_Start,MOB_End,Approach,Param1,Param2,Explanation
NON PRIME,ALL,Coll_Principal,0,12,DonorCohort,202404,,Young-donor
NON PRIME,ALL,Coll_Principal,13,36,CohortTrend,6,,Mid-trend
NON PRIME,ALL,Coll_Principal,37,999,CohortAvg,6,,Mature-flat
```

### Key Fields
- **Segment**: NON PRIME, NRP-S, NRP-M, NRP-L, PRIME, or ALL
- **Cohort**: Specific cohort (e.g., 202509) or ALL
- **Metric**: Coll_Principal, Coll_Interest, InterestRevenue, WO_DebtSold, etc.
- **MOB_Start/MOB_End**: Range of MOBs this rule applies to
- **Approach**: DonorCohort, CohortTrend, CohortAvg, SegMedian, Manual
- **Param1/Param2**: Parameters for the approach

## Common Issues and Fixes

### Issue 1: MOB 0 Anomaly
**Symptom**: First month of new cohort shows extreme rates (e.g., -49% collections)
**Cause**: Low opening GBV with normal collections creates artificially high rate
**Fix**: Override with DonorCohort or Manual rate for MOB 0

### Issue 2: CohortTrend Explosion
**Symptom**: Rates escalate to unrealistic levels (e.g., -40%+ collections)
**Cause**: CohortTrend extrapolating from limited or anomalous data
**Fix**: Extend DonorCohort usage, or switch to CohortAvg for that cohort

Example fix in Rate_Methodology.csv:
```csv
NON PRIME,202509,Coll_Principal,13,999,DonorCohort,202508,,Fix-202509-trend
```

### Issue 3: Rate Curve Discontinuity
**Symptom**: Sudden jump in rates at specific MOB (e.g., MOB 13)
**Cause**: Methodology switch from DonorCohort to CohortTrend
**Fix**: Ensure target cohort's historical data is clean, or extend DonorCohort

## Output Files

### BB Forecast Baseline Outputs.xlsx Sheets

| Sheet | Purpose |
|-------|---------|
| 1_Actuals_Data | Raw historical data |
| 2_Historical_Rates | Calculated rates from actuals |
| 3_Extended_Curves | Rates extrapolated to future MOBs |
| 4_Methodology_Applied | Which approach was used for each cell |
| 5_Forecast_Output | Final forecast with all cash flows |
| 6_Combined_View | Actuals + Forecast combined |
| 7_Rate_Methodology_Rules | Rules that were applied |
| Coll Total Rates | Pivot of collection rates |
| Forecast vs Budget P&L | Comparison to budget |

## Debugging Workflow

### 1. Identify the Problem
```python
# Find cohorts/MOBs with unusual rates
v32 = pd.read_excel('BB Forecast Baseline Outputs v3.2.xlsx', sheet_name='5_Forecast_Output')
v32['Rate'] = (v32['Coll_Principal'] + v32['Coll_Interest']) / v32['OpeningGBV']

# Flag extreme rates
v32[abs(v32['Rate']) > 0.15]  # Rates > 15%
```

### 2. Check Methodology Applied
```python
# See what approach was used
meth = pd.read_excel('BB Forecast Baseline Outputs v3.2.xlsx', sheet_name='4_Methodology_Applied')
meth[(meth['Cohort'] == 202509) & (meth['Segment'] == 'NON PRIME')]
```

### 3. Check Historical Data
```python
# Verify historical rates are sensible
hist = pd.read_excel('BB Forecast Baseline Outputs v3.2.xlsx', sheet_name='2_Historical_Rates')
hist[(hist['Cohort'] == 202509)]
```

### 4. Implement Fix
Update `Rate_Methodology.csv` with override rule, then re-run model.

## Tips

- Always validate rate curves visually before finalizing forecasts
- New cohorts (< 6 months old) should always use DonorCohort
- Watch for MOB 0 anomalies in every new cohort
- CohortTrend needs at least 6+ months of clean data to work well
- Test methodology changes on individual cohorts before applying broadly
