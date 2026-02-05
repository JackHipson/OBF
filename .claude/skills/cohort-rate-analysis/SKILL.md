---
name: cohort-rate-analysis
description: Analyze loan portfolio rates by cohort, segment, and MOB. Use when investigating collection rates, revenue rates, coverage ratios, understanding rate trends, or comparing cohort performance.
argument-hint: "[rate-type] [cohort/segment]"
---

# Cohort Rate Analysis

Analyze loan portfolio rates across cohorts, segments, and months-on-book (MOB).

## When to Use This Skill

- Investigating collection rate trends
- Comparing cohort performance
- Understanding rate curves by MOB
- Identifying cohorts with anomalous behavior
- Analyzing coverage ratio trends

## Key Dimensions

### Segments
| Segment | Description |
|---------|-------------|
| NON PRIME | Highest risk tier |
| NRP-S | Near Prime Small |
| NRP-M | Near Prime Medium |
| NRP-L | Near Prime Large |
| PRIME | Lowest risk tier |

### Cohort
- Format: YYYYMM (e.g., 202509 = September 2025)
- Represents when loans were originated
- Older cohorts have more history

### MOB (Month-on-Book)
- Age of the cohort in months
- MOB 0 = First month of origination
- MOB 12 = One year old
- Higher MOB = more mature

## Key Rate Types

### 1. Collection Rates
```python
Coll_Principal_Rate = Coll_Principal / OpeningGBV
Coll_Interest_Rate = Coll_Interest / OpeningGBV
Coll_Total_Rate = (Coll_Principal + Coll_Interest) / OpeningGBV
```

**Expected patterns**:
- Rates are NEGATIVE (collections reduce GBV)
- Typical range: -5% to -10% per month
- Generally increase (more negative) with MOB as loans mature
- Newer cohorts may have lower rates initially

### 2. Revenue Rates
```python
InterestRevenue_Rate = InterestRevenue / OpeningGBV
```

**Expected patterns**:
- Rates are POSITIVE (revenue accrues to GBV)
- Typical range: 2% to 5% per month
- May decrease with MOB as loans pay down

### 3. Write-Off Rates
```python
WO_DebtSold_Rate = WO_DebtSold / OpeningGBV
WO_Other_Rate = WO_Other / OpeningGBV
```

**Expected patterns**:
- Rates are NEGATIVE (write-offs reduce GBV)
- Debt sales typically quarterly
- Other write-offs usually small

### 4. Coverage Ratio
```python
Coverage_Ratio = Provision / GBV
```

**Expected patterns**:
- Typical range: 8% to 15%
- Higher for riskier segments (NON PRIME)
- May increase with MOB for seasoning cohorts

## Analysis Code Patterns

### Load Data
```python
import pandas as pd

# Load actuals
actuals = pd.read_excel('Fact_Raw_New.xlsx')
actuals['Month'] = pd.to_datetime(actuals['calendarmonth'].astype(str), format='%Y%m')
actuals['CohortMonth'] = pd.to_datetime(actuals['cohort'].astype(str), format='%Y%m', errors='coerce')
actuals['MOB'] = ((actuals['Month'].dt.year - actuals['CohortMonth'].dt.year) * 12 +
                  (actuals['Month'].dt.month - actuals['CohortMonth'].dt.month))
```

### Calculate Rates by Cohort/Segment/MOB
```python
# Aggregate by cohort, segment, MOB
rates = actuals.groupby(['cohort', 'lob', 'MOB']).agg({
    'openinggbv': 'sum',
    'principalcollections': 'sum',
    'interestcollections': 'sum',
    'interestrevenue': 'sum'
}).reset_index()

rates['Coll_Total_Rate'] = (rates['principalcollections'] + rates['interestcollections']) / rates['openinggbv']
rates['Revenue_Rate'] = rates['interestrevenue'] / rates['openinggbv']
```

### Compare Cohorts at Same MOB
```python
# Compare all cohorts at MOB 12
mob_12 = rates[rates['MOB'] == 12]
mob_12.sort_values(['lob', 'Coll_Total_Rate'])
```

### Identify Anomalies
```python
# Find rates outside normal range
anomalies = rates[
    (abs(rates['Coll_Total_Rate']) > 0.15) |  # > 15% collection rate
    (rates['Coll_Total_Rate'] > 0)             # Positive (should be negative)
]
```

## Common Anomalies

### MOB 0 Anomaly
**What it looks like**: Extremely high rates at MOB 0 (e.g., -49%)
**Why it happens**: Low opening GBV (new cohort just starting) with normal collection activity
**How to handle**: Use DonorCohort methodology or exclude MOB 0 from trend calculations

### Cohort Vintage Effect
**What it looks like**: Certain cohort years perform consistently better/worse
**Why it happens**: Economic conditions, underwriting changes, product mix
**How to handle**: Segment analysis by cohort vintage, adjust forecasts accordingly

### Seasonal Patterns
**What it looks like**: Rates vary by calendar month
**Why it happens**: Payment timing, holidays, bonus periods
**How to handle**: Include seasonal factors in forecasts

## Visualization Approaches

### Rate Curves by Cohort
```python
import matplotlib.pyplot as plt

for cohort in ['202401', '202407', '202501']:
    cohort_data = rates[rates['cohort'] == cohort]
    plt.plot(cohort_data['MOB'], cohort_data['Coll_Total_Rate'], label=cohort)

plt.xlabel('MOB')
plt.ylabel('Collection Rate')
plt.legend()
plt.title('Collection Rate Curves by Cohort')
```

### Heatmap by Cohort × MOB
```python
import seaborn as sns

pivot = rates.pivot_table(
    values='Coll_Total_Rate',
    index='cohort',
    columns='MOB'
)
sns.heatmap(pivot, cmap='RdYlGn_r', center=-0.07)
```

## Output Format

```
================================================================================
RATE ANALYSIS: [Rate Type] by [Dimension]
================================================================================

SUMMARY:
  Average Rate:     X.XX%
  Rate Range:       X.XX% to X.XX%
  Trend:            [Increasing/Decreasing/Stable]

BY SEGMENT:
  NON PRIME:        X.XX%
  NRP-S:            X.XX%
  NRP-M:            X.XX%
  NRP-L:            X.XX%
  PRIME:            X.XX%

BY MOB:
  MOB 1-6:          X.XX% (avg)
  MOB 7-12:         X.XX% (avg)
  MOB 13-24:        X.XX% (avg)
  MOB 25+:          X.XX% (avg)

ANOMALIES IDENTIFIED:
  - [Cohort] at MOB [X]: [Description]

RECOMMENDATIONS:
  - [Actions based on analysis]
```

## Tips

- Always validate rates are in expected ranges before analysis
- Check for inf/NaN values from division by zero (low GBV cohorts)
- Compare same-MOB rates across cohorts for fair comparison
- Account for cohort size (GBV) when averaging rates
- Rate curves should generally be smooth - jumps indicate data issues
