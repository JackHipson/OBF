# Forecast vs Actuals Sheet - Complete Analysis

## Summary

I've analyzed the "forecast vs actuals" sheet from your Forecast Baseline Outputs workbook and mapped out its complete structure. Here's what I found and created for you.

---

## Quick Answer: Sheet Structure

The sheet has **4 main sections** across 682 rows:

1. **Rows 1-48**: BB Forecast (detailed by metric × segment)
2. **Rows 49-193**: BB Forecast Summary & percentages
3. **Rows 194-368**: ACTUALS (total book) ← **This is what you need**
4. **Rows 369-682**: VARIANCES (forecast minus actuals)

---

## Key Finding: Where Your Data Is

### BB Forecast Data
- **Starts at**: Column Q (Oct 2025)
- **Row structure**: Columns O & P contain labels (metric names and segments)
- **Data columns**: Q onwards (monthly forecasts from Oct 2025)

### Total Book Actuals Data
- **Starts at**: Row 194 (marked with "ACTUALS (total book)>>>")
- **Months covered**: Jan 2025 - Sep 2025 (Columns H-P)
- **Row structure**: Column F contains metric labels
- **Data columns**: H = Jan, I = Feb, J = Mar, ..., P = Sep

### Important Note on Column Overlap
Columns O and P serve dual purposes:
- In **forecast section** (rows 1-48): They're label columns (metric names & segments)
- In **actuals section** (rows 194+): They're data columns (Aug & Sep 2025)

---

## Top 10 Key Metrics (Row Numbers)

| Metric | Row | Section |
|--------|-----|---------|
| Total Collections (Principal + Interest) | **200** | Actuals |
| Total Collections inc Contra | **222** | Actuals |
| Closing GBV | **240** | Actuals |
| Average GBV | **250** | Actuals |
| Closing NBV | **260** | Actuals |
| Average NBV | **270** | Actuals |
| Revenue | **280** | Actuals |
| Gross Impairment | **291** | Actuals |
| Net Impairment | **339** | Actuals |
| RAM (incl. debt sale gain) | **355** | Actuals |

---

## Month Column Mapping

```
Column H = Jan 2025
Column I = Feb 2025
Column J = Mar 2025
Column K = Apr 2025
Column L = May 2025
Column M = Jun 2025
Column N = Jul 2025
Column O = Aug 2025 (dual-purpose column)
Column P = Sep 2025 (dual-purpose column)
Column Q = Oct 2025 (forecast starts here)
```

---

## Files Created for You

### 1. Documentation

| File | Purpose |
|------|---------|
| **`SHEET_STRUCTURE_SUMMARY.md`** | Complete detailed map of all sections |
| **`QUICK_REFERENCE_METRICS.md`** | Quick lookup for specific metric row numbers |
| **`README_FORECAST_VS_ACTUALS.md`** | This file - executive summary |

### 2. Python Scripts

| Script | Purpose |
|--------|---------|
| **`extract_key_metrics.py`** | Ready-to-use script to extract and analyze key metrics |
| `parse_fva_sheet.py` | Dumps raw cell values (diagnostic) |
| `analyze_fva_structure.py` | Identifies section markers (diagnostic) |
| `examine_actuals_section.py` | Examines actuals section (diagnostic) |
| `complete_sheet_structure.py` | Maps complete structure (diagnostic) |

### 3. Data Export

| File | Content |
|------|---------|
| **`actuals_key_metrics.csv`** | Extracted actuals data (Jan-Sep 2025) for 10 key metrics |

---

## How to Use the Extract Script

**File**: `/home/user/OBF/extract_key_metrics.py`

### Run it:
```bash
python /home/user/OBF/extract_key_metrics.py
```

### What it does:
1. Opens the workbook
2. Extracts 10 key metrics for Jan-Sep 2025 actuals
3. Prints a formatted table
4. Exports to CSV (`actuals_key_metrics.csv`)
5. Shows example calculations (e.g., Collections as % of Avg GBV)
6. Shows segment breakdowns

### Sample output:
```
Sep 2025 Collections as % of Avg GBV: 6.92%

Sep 2025 Collections by Segment:
  Non Prime: 10,898,384.08
  Near Prime Small: 3,156,787.97
  Near Prime Medium: 4,748,316.63
  Prime: 301,396.22
```

---

## Common Use Cases

### Use Case 1: Get Total Collections for a Specific Month
```python
import openpyxl

wb = openpyxl.load_workbook("Forecast Baseline Outputs v3.6 (new collections & impairment).xlsx", data_only=True)
ws = wb["forecast vs actuals"]

# March 2025 Total Collections
march_collections = ws['J200'].value  # Row 200, Column J
print(f"March 2025 Collections: {march_collections:,.2f}")

wb.close()
```

### Use Case 2: Get All Months for a Metric
```python
from openpyxl.utils import get_column_letter

# Loop through Jan-Sep 2025 (Columns H-P)
for col_num in range(8, 17):  # H=8, P=16
    col_letter = get_column_letter(col_num)
    value = ws[f'{col_letter}200'].value  # Row 200 = Total Collections
    month = ws[f'{col_letter}1'].value
    print(f"{month}: {value:,.2f}")
```

### Use Case 3: Calculate Derived Metrics
```python
# Collections as % of Average GBV for Sep 2025
sep_collections = ws['P200'].value  # Row 200, Column P
sep_avg_gbv = ws['P250'].value      # Row 250, Column P

if sep_collections and sep_avg_gbv:
    coll_pct = (sep_collections / sep_avg_gbv) * 100
    print(f"Collections % of GBV: {coll_pct:.2f}%")
```

---

## Actuals Section - Complete Metric List

### Collections Metrics (Rows 196-227)
- 196-199: Principal + Interest by segment
- **200**: TOTAL Principal + Interest
- 202-205: as % of avg GBV (by segment)
- 207-210: Contra collections by segment
- **211**: TOTAL Contra collections
- 213-216: Contra as % of avg GBV
- 218-221: Total collections inc contra (by segment)
- **222**: TOTAL Collections inc contra
- 224-227: Total coll as % of avg GBV

### Balance Sheet Metrics (Rows 240-270)
- **240**: Closing GBV
- 241-244: Segment mix %
- 246-249: Average GBV by segment
- **250**: Average GBV TOTAL
- **260**: Closing NBV
- **270**: Average NBV

### P&L Metrics (Rows 280-361)
- **280**: Revenue
- 281: as % of average GBV
- **291**: Gross Impairment
- 292, 297: Gross impairment as % of revenue/GBV
- **307**: RAM (excl. debt sale gain)
- 308, 313: RAM as % of revenue/GBV
- **323**: Debt Sale Gain
- 324, 329: DS gain as % of gross impairment/GBV
- **339**: Net Impairment
- 340, 345: Net impairment as % of gross impairment/GBV
- **355**: RAM (incl. debt sale gain)
- 356, 361: RAM (incl) as % of revenue/GBV

---

## Segments Breakdown

All metrics are broken down by these segments:

1. **Non Prime** - Total non-prime loans
2. **Near Prime Small (NRP-S)** - Small near-prime loans
3. **Near Prime Medium (NRP-M)** - Medium near-prime loans
4. **Near Prime Large (NRP-L)** - Large near-prime loans
5. **Prime** - Prime loans

---

## Next Steps / Recommendations

1. **Use the extraction script** (`extract_key_metrics.py`) as a template for your analysis
2. **Modify it** to pull the specific metrics you need
3. **Automate** monthly reporting by running this script after updating the workbook
4. **Consider** creating a dashboard that reads from the CSV output

---

## Notes & Caveats

1. **Data quality**: Some metrics (Closing NBV, Net Impairment) showed as None in the sample extraction. You may need to verify these rows have data in the expected columns.

2. **Column overlap**: Be careful with columns O and P - they mean different things in different sections of the sheet.

3. **Date alignment**: BB Forecast starts from Oct 2025 (Column Q), while Actuals start from Jan 2025 (Column H). This is by design for forecast vs actuals comparison.

4. **Openpyxl warning**: You'll see a warning about "Slicer List extension" - this is harmless and can be ignored.

---

## Questions to Consider

1. **Which metrics** do you need to track most frequently?
2. **What frequency** do you need this data (monthly, weekly, ad-hoc)?
3. **What format** works best for your downstream analysis (CSV, Excel, database)?
4. **Do you need** segment-level detail or just totals?

Let me know if you'd like me to:
- Customize the extraction script for specific metrics
- Create automated reports
- Build a dashboard
- Explain any specific metrics in more detail

---

**Generated**: 2026-02-10
**By**: Claude (via Claude Code)
**For**: Jack Hipson - Oakbrook Finance

**File Path**: `/home/user/OBF/README_FORECAST_VS_ACTUALS.md`
