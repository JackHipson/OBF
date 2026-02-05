---
name: nbv-gbv-reconciliation
description: Reconcile NBV (Net Book Value) and GBV (Gross Book Value) calculations. Use when investigating NBV variances, analyzing provision movements, understanding coverage ratio changes, or reconciling balance sheet items.
argument-hint: "[analysis-type] [period]"
---

# NBV/GBV Reconciliation

Reconcile and analyze the relationship between GBV and NBV in loan portfolios.

## When to Use This Skill

- Investigating NBV variances vs budget
- Understanding why NBV moves differently than GBV
- Analyzing provision and coverage ratio changes
- Reconciling balance sheet items
- Explaining NBV to stakeholders

## Key Relationships

### Fundamental Formula
```
NBV = GBV - Provision
```

Where:
- **GBV (Gross Book Value)**: Total loan balances outstanding
- **Provision**: Expected credit losses held against the portfolio
- **NBV (Net Book Value)**: GBV after deducting provision

### Coverage Ratio
```
Coverage Ratio = Provision / GBV
```

Typical ranges by segment:
| Segment | Coverage Ratio |
|---------|----------------|
| PRIME | 0% - 3% |
| NRP-L | 5% - 10% |
| NRP-M | 2% - 5% |
| NRP-S | 5% - 8% |
| NON PRIME | 15% - 25% |

## GBV Movement Analysis

### Closing GBV Formula
```
ClosingGBV = OpeningGBV
           + Coll_Principal        (negative - reduces GBV)
           + Coll_Interest         (negative - reduces GBV)
           + WO_DebtSold           (negative - reduces GBV)
           + WO_Other              (negative - reduces GBV)
           + ContraSettlements_P   (negative - in actuals; £0 in BB model)
           + ContraSettlements_I   (negative - in actuals; £0 in BB model)
           + NewLoanAmount         (positive - in actuals; £0 in BB model)
           + InterestRevenue       (positive - accrued interest)
```

### GBV Bridge Waterfall
```
Opening GBV:           £XXX.XM
+ Interest Accrued:    £XX.XM
- Collections:         £(XX.X)M
- Write-offs:          £(X.X)M
- Contra Settlements:  £(X.X)M   (actuals only)
+ New Loans:           £XX.XM    (actuals only)
= Closing GBV:         £XXX.XM
```

## NBV Movement Analysis

### NBV Change Drivers
```
NBV Change = GBV Change - Provision Change
```

Or equivalently:
```
NBV Change = GBV Change - (Gross Impairment - Provision Releases)
```

### Provision Movement Components
1. **Gross Impairment**: New provision charges
2. **Debt Sale Releases**: Provision released when loans written off
3. **Coverage Ratio Changes**: Changes in ECL assumptions
4. **Mix Effects**: Segment composition changes

## Analysis Code Patterns

### Load and Calculate NBV
```python
import pandas as pd

# Load actuals
actuals = pd.read_excel('Fact_Raw_New.xlsx')
actuals['Month'] = pd.to_datetime(actuals['calendarmonth'].astype(str), format='%Y%m')

# Monthly totals
monthly = actuals.groupby('Month').agg({
    'closinggbv': 'sum',
    'provisionatmonthend': 'sum',  # Often stored as negative
}).reset_index()

# Calculate NBV (provision usually stored as negative)
monthly['NBV'] = monthly['closinggbv'] + monthly['provisionatmonthend']
monthly['CoverageRatio'] = abs(monthly['provisionatmonthend']) / monthly['closinggbv']
```

### Compare Model vs Actuals
```python
# Load model
model = pd.read_excel('BB Forecast Baseline Outputs v3.2.xlsx', sheet_name='5_Forecast_Output')
model_monthly = model.groupby('ForecastMonth').agg({
    'ClosingGBV': 'sum',
    'ClosingNBV': 'sum'
}).reset_index()
model_monthly['Provision'] = model_monthly['ClosingGBV'] - model_monthly['ClosingNBV']
model_monthly['CoverageRatio'] = model_monthly['Provision'] / model_monthly['ClosingGBV']

# Compare coverage ratios
print("Actuals Coverage:", actuals_coverage)
print("Model Coverage:", model_coverage)
```

### Analyze Provision Movement
```python
# Month-over-month provision change
monthly['Provision_Change'] = monthly['provisionatmonthend'].diff()

# Decompose into components
monthly['GBV_Change'] = monthly['closinggbv'].diff()
monthly['NBV_Change'] = monthly['NBV'].diff()
monthly['Coverage_Effect'] = monthly['CoverageRatio'].diff() * monthly['closinggbv']
```

## Common NBV Variance Drivers

### 1. Collection Rate Differences
**Impact**: Higher collections → Lower GBV → Lower NBV
```
GBV Impact = Collection Rate Variance × GBV Base
NBV Impact ≈ GBV Impact × (1 - Coverage Ratio)
```

### 2. Coverage Ratio Changes
**Impact**: Higher coverage → Higher provision → Lower NBV
```
Provision Impact = Coverage Ratio Change × GBV
NBV Impact = -Provision Impact
```

### 3. Debt Sale Timing
**Impact**: Debt sales reduce GBV and release provision
```
GBV Impact = Write-off Amount (negative)
Provision Impact = Write-off Amount × Coverage on those loans (negative)
NBV Impact = GBV Impact - Provision Impact (usually small net)
```

### 4. Contra Settlements (BB vs Total)
**Impact**: BB model keeps loans; actuals show them gone
```
BB Model: Loan stays on book → Higher GBV
Actuals: Loan contra-settled → Lower GBV
Variance = Contra settlement amount
```

### 5. Mix Effects
**Impact**: Shift toward higher/lower risk segments changes blended coverage
```
Coverage Change = Σ (Segment Mix Change × Segment Coverage)
```

## Reconciliation Framework

### Step 1: Calculate Variances
```
GBV Variance = Actual GBV - Budget GBV
NBV Variance = Actual NBV - Budget NBV
Provision Variance = Actual Provision - Budget Provision
Coverage Variance = Actual Coverage - Budget Coverage
```

### Step 2: Decompose NBV Variance
```
NBV Variance = GBV Variance × (1 - Coverage) + Coverage Variance × GBV
            = GBV Effect + Coverage Effect
```

### Step 3: Attribute to Drivers
```
GBV Effect contributors:
  - Collection rate differences
  - Write-off timing
  - Contra settlements (if comparing to actuals)
  - New loans (if comparing to total book)

Coverage Effect contributors:
  - ECL model changes
  - Segment mix changes
  - Risk migration
```

## Output Format

```
================================================================================
NBV RECONCILIATION: [Period]
================================================================================

SUMMARY:
                    Budget      Actual      Variance
  GBV:              £XXX.XM     £XXX.XM     £(X.X)M
  Provision:        £XX.XM      £XX.XM      £X.XM
  NBV:              £XXX.XM     £XXX.XM     £(X.X)M
  Coverage:         X.X%        X.X%        X.Xpp

VARIANCE DECOMPOSITION:
  GBV Effect:                   £(X.X)M
    - Collections variance:     £(X.X)M
    - Write-off timing:         £(X.X)M
    - Contra settlements:       £(X.X)M

  Coverage Effect:              £(X.X)M
    - ECL assumption changes:   £(X.X)M
    - Mix effects:              £(X.X)M

  TOTAL NBV VARIANCE:           £(X.X)M

RECONCILIATION CHECK:
  GBV Effect + Coverage Effect = £(X.X)M
  Actual NBV Variance = £(X.X)M
  Difference: £X.XM (should be ~£0)
```

## Tips

- Always verify sign conventions (provision often stored as negative)
- Check if comparing like-for-like (BB only vs BB only)
- Debt sales cause simultaneous GBV and provision movements
- Coverage ratio changes can offset or amplify GBV changes
- Mix effects can be significant when segment composition shifts
- Model assumes stable/increasing coverage; actuals may show volatility
