---
name: contra-settlement-analysis
description: Analyze contra settlements from loan top-ups. Use when investigating top-up impacts, understanding BB vs FB splits, reconciling total book GBV, or explaining contra settlement variances.
argument-hint: "[analysis-type] [period]"
---

# Contra Settlement Analysis

Analyze contra settlements arising from loan top-ups and their impact on portfolio metrics.

## When to Use This Skill

- Understanding how top-ups affect BB and FB models
- Reconciling total book GBV between model and actuals
- Explaining variances caused by contra settlements
- Analyzing top-up activity trends

## What Are Contra Settlements?

When a customer does a **top-up** on an existing loan:

1. **Old Agreement**: The existing loan is "contra-settled" (closed out)
2. **New Agreement**: A new loan is created with combined balance
3. **Net Effect**: Customer has one loan with higher balance

### Example
```
Before Top-Up:
  - Existing loan balance: £5,000 (on Backbook)

Top-Up Request:
  - Additional cash requested: £2,000

After Top-Up:
  - Old loan: £0 (contra-settled)
  - New loan: £7,000 (on Frontbook)
  - Contra settlement amount: £5,000
  - Top-up increment: £2,000
```

## BB/FB Model Treatment

### By Design (Budget Assumption)
```
Backbook Model:
  - ContraSettlements_Principal = £0
  - ContraSettlements_Interest = £0
  - Old loan balances REMAIN on BB (not removed)

Frontbook Model:
  - NewLoanAmount = Top-up increment only (£2,000 in example)
  - Does NOT include the contra-settled portion

Total Book = BB + FB = £5,000 + £2,000 = £7,000 ✓
```

### In Reality (Actuals)
```
Actuals show:
  - principalcontrasettlement: -£5,000 (removes old loan from BB)
  - New loan: £7,000 (full amount on FB)

Total Book = £7,000 ✓
```

### Key Insight
Both approaches give the same **Total Book** result, but:
- **Model**: BB keeps old loan, FB has increment only
- **Actuals**: BB loses old loan (contra-settled), FB has full new loan

This creates a variance when comparing **BB model to BB actuals** (but not Total Book).

## Data Sources

### Actuals Columns
```python
actuals['principalcontrasettlement']      # Principal portion contra-settled
actuals['nonprincipalcontrasettlement']   # Interest/fees contra-settled
```

### Model Columns
```python
model['ContraSettlements_Principal']      # Always £0 in BB model
model['ContraSettlements_Interest']       # Always £0 in BB model
model['NewLoanAmount']                    # Always £0 in BB model
```

## Analysis Code Patterns

### Calculate Contra Settlement Activity
```python
import pandas as pd

actuals = pd.read_excel('Fact_Raw_New.xlsx')
actuals['Month'] = pd.to_datetime(actuals['calendarmonth'].astype(str), format='%Y%m')

# Monthly contra settlements
monthly = actuals.groupby('Month').agg({
    'openinggbv': 'sum',
    'principalcontrasettlement': 'sum',
    'nonprincipalcontrasettlement': 'sum',
}).reset_index()

monthly['Total_Contra'] = (monthly['principalcontrasettlement'] +
                           monthly['nonprincipalcontrasettlement'])
monthly['Contra_Rate'] = monthly['Total_Contra'] / monthly['openinggbv']
```

### Compare to Model
```python
# Model assumes contra settlements = £0
model = pd.read_excel('BB Forecast Baseline Outputs v3.2.xlsx', sheet_name='5_Forecast_Output')
model_contra = model['ContraSettlements_Principal'].sum()  # Should be £0

print(f"Model contra settlements: £{model_contra:,.0f}")
print(f"Actual contra settlements: £{abs(monthly['Total_Contra'].sum()):,.0f}")
print(f"Variance: £{abs(monthly['Total_Contra'].sum()) - model_contra:,.0f}")
```

### Analyze by Cohort Age
```python
# Contra settlements by cohort vintage
actuals['CohortYear'] = actuals['cohort'].apply(
    lambda x: int(str(x)[:4]) if str(x).isdigit() else 0
)

by_vintage = actuals.groupby('CohortYear').agg({
    'principalcontrasettlement': 'sum',
    'openinggbv': 'sum'
}).reset_index()

by_vintage['Contra_Rate'] = by_vintage['principalcontrasettlement'] / by_vintage['openinggbv']
```

## Typical Contra Settlement Patterns

### By Volume
- Typical rate: 1.0% - 1.5% of GBV per month
- Annual volume: ~£35-40M on a £275M portfolio
- Varies with top-up marketing campaigns

### By Cohort Age
| Cohort Age | Contra Rate | Explanation |
|------------|-------------|-------------|
| 0-6 months | Low (~0.3%) | New loans rarely topped up immediately |
| 6-12 months | Medium (~1.0%) | Customers becoming eligible for top-ups |
| 12-24 months | High (~1.5%) | Peak top-up activity |
| 24+ months | Medium (~1.0%) | Mature loans, some already topped up |

### Seasonality
- Higher in Q4 (Christmas spending)
- Higher in Q1 (new year, tax refunds)

## Variance Analysis Framework

### BB Model vs BB Actuals Variance
```
BB Model GBV:     Higher (loans stay on book)
BB Actuals GBV:   Lower (loans contra-settled out)
Variance:         = Contra settlement amount

This is EXPECTED by design, not an error.
```

### Total Book Reconciliation
```
Model Total:  BB Model GBV + FB Model GBV (increment only)
Actual Total: BB Actual GBV + FB Actual GBV (full new loans)

These should reconcile if:
  Model BB (keeps loan) + Model FB (increment) = Actual Total

Check: Model Total ≈ Actual Total ✓
```

## Output Format

```
================================================================================
CONTRA SETTLEMENT ANALYSIS: [Period]
================================================================================

SUMMARY:
  Total Contra Settlements:     £XX.XM
  Average Monthly Rate:         X.X% of GBV

MONTHLY TREND:
  Month        GBV         Contra      Rate
  -------     -------     -------     ------
  2025-10     £XXX.XM     £X.XM       X.X%
  2025-11     £XXX.XM     £X.XM       X.X%
  ...

MODEL vs ACTUALS:
  Model assumes:                £0 contra settlements
  Actuals show:                 £XX.XM contra settlements
  Expected BB variance:         £XX.XM (model higher)

TOTAL BOOK CHECK:
  Model Total (BB + FB):        £XXX.XM
  Actual Total:                 £XXX.XM
  Reconciliation:               ✓ Matches / ✗ Gap of £X.XM

BY COHORT VINTAGE:
  Pre-2024 (Backbook):          £X.XM (XX%)
  2024+ (Frontbook):            £X.XM (XX%)
```

## Key Points to Remember

1. **BB model has £0 contra settlements by design** - this is intentional, not a bug

2. **Total book should reconcile** - the variance only appears at BB level, not Total

3. **Contra settlements explain BB variance** - when stakeholders ask why BB actuals differ from model, contra settlements are often a major driver

4. **Top-up increment goes to FB** - only the additional cash goes to Frontbook, not the full new loan (in the model design)

5. **Actuals treatment differs** - actuals show full new loan on FB and contra settlement removing old from BB

## Tips

- Always clarify whether analyzing BB only or Total Book
- Contra settlement variance is expected, not an error
- Track top-up activity as a leading indicator
- Higher top-up rates mean faster BB runoff (in actuals)
- Model assumes stable contra rate of 0% - actuals show ~1-1.5%
