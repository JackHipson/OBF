# Quick Reference - Key Metric Row Numbers

## File: Forecast Baseline Outputs v3.6 (new collections & impairment).xlsx
## Sheet: forecast vs actuals

---

## BB FORECAST DATA (Rows 1-193)

### Detailed Forecast by Metric x Segment (Rows 5-44)

| Metric | Row | Segments in Rows Below |
|--------|-----|------------------------|
| **Opening GBV** | 5 | 6-9 (NRP-L, NRP-M, NRP-S, PRIME) |
| **Collections Principal** | 10 | 11-14 |
| **Collections Interest** | 15 | 16-19 |
| **Closing GBV** | 20 | 21-24 |
| **Closing NBV** | 25 | 26-29 |
| **Interest Revenue** | 30 | 31-34 |
| **Gross Impairment (Excl DS)** | 35 | 36-39 |
| **Net Impairment** | 40 | 41-44 |

**Data columns**: Column Q onwards (starting Oct 2025)

### Forecast Summary (Rows 49-193)

| Metric | Row |
|--------|-----|
| **Section Header** | 49 |
| **BB Collections by Segment** | 51-54 |
| BB coll + principal collections | 55 |
| as % of average closing GBV | 56-60 |
| **BB Closing GBV** | 66 |
| Segment Mix % | 67-70 |
| BB Average GBV | 76 |
| **BB Closing NBV** | 86 |

**Data columns**: Column Q onwards (starting Oct 2025)

---

## ACTUALS DATA (Rows 194-368)

### Collections

| Metric | Row | Notes |
|--------|-----|-------|
| **Section Header** | 194 | "ACTUALS (total book)>>>" |
| **Principal + Interest Collections** | | |
| - Non Prime | 196 | |
| - Near Prime Small | 197 | |
| - Near Prime Medium | 198 | |
| - Prime | 199 | |
| **TOTAL Principal + Interest** | **200** | **KEY METRIC** |
| | | |
| **Collections as % of avg GBV** | 202-205 | By segment |
| | | |
| **Contra Collections** | | |
| - Non Prime | 207 | |
| - Near Prime Small | 208 | |
| - Near Prime Medium | 209 | |
| - Prime | 210 | |
| **Total Contra Collections** | **211** | |
| | | |
| **Contra as % of avg GBV** | 213-216 | By segment |
| | | |
| **Total Collections (inc contra)** | | |
| - Non Prime | 218 | |
| - Near Prime Small | 219 | |
| - Near Prime Medium | 220 | |
| - Prime | 221 | |
| **TOTAL Collections inc Contra** | **222** | **KEY METRIC** |
| | | |
| **Total coll as % of avg GBV** | 224-227 | By segment |

### Balance Sheet Metrics

| Metric | Row | Notes |
|--------|-----|-------|
| **Closing GBV** | **240** | **KEY METRIC** |
| Segment Mix (GBV) | 241-244 | |
| | | |
| **Average GBV by Segment** | 246-249 | |
| **Average GBV TOTAL** | **250** | **KEY METRIC** |
| | | |
| **Closing NBV** | **260** | **KEY METRIC** |
| | | |
| **Average NBV** | **270** | **KEY METRIC** |

### P&L Metrics

| Metric | Row | Notes |
|--------|-----|-------|
| **Revenue** | **280** | **KEY METRIC** |
| Total as % of average GBV | 281 | |

### Impairment Metrics

| Metric | Row | Notes |
|--------|-----|-------|
| **Total Gross Impairment** | **291** | **KEY METRIC** |
| as % of revenue | 292 | |
| as % of average GBV | 297 | |
| | | |
| **RAM (excl. debt sale gain)** | **307** | **KEY METRIC** |
| as % of revenue | 308 | |
| as % of average GBV | 313 | |
| | | |
| **Debt Sale Gain** | **323** | |
| as % gross impairment | 324 | |
| as % of average GBV | 329 | |
| | | |
| **Net Impairment** | **339** | **KEY METRIC** |
| as % gross impairment | 340 | |
| as % of average GBV | 345 | |
| | | |
| **RAM (incl. debt sale gain)** | **355** | **KEY METRIC** |
| as % of revenue | 356 | |
| as % of average GBV | 361 | |

**Data columns**: Column H (Jan 2025) through Column P (Sep 2025) and beyond

---

## VARIANCES (Rows 369-682)

| Metric | Row | Notes |
|--------|-----|-------|
| **Section Header** | 369 | "VARIANCES (forecast minus actuals)>>>" |
| | | |
| **Collections Variances** | 372-375 | By segment |
| BB total collections variance | 376 | |
| as % of average closing GBV | 377-381 | |
| | | |
| **BB Closing GBV Variance** | 387 | |
| | | |
| *(Structure mirrors actuals section)* | 388+ | |

**Data columns**: Variance = Forecast (Column Q+) - Actuals (Column H-P)

---

## Column Reference - Month Mapping

### For ACTUALS (Rows 194-368)
```
Column H = Jan 2025
Column I = Feb 2025
Column J = Mar 2025
Column K = Apr 2025
Column L = May 2025
Column M = Jun 2025
Column N = Jul 2025
Column O = Aug 2025 (Note: Column O is dual-purpose)
Column P = Sep 2025 (Note: Column P is dual-purpose)
Column Q = Oct 2025
```

### For FORECAST (Rows 1-193)
```
Column Q = Oct 2025 (FIRST forecast month)
Column R = Nov 2025
Column S = Dec 2025
Column T = Jan 2026
Column U = Feb 2026
Column V = Mar 2026
...and so on
```

### Summary Column
```
Column BF (58) = FY26 summary/total
```

---

## Usage Examples

### Example 1: Get Total Collections (Actuals) for March 2025
- **Row**: 200 (TOTAL Principal + Interest)
- **Column**: J (Mar 2025)
- **Cell**: J200

### Example 2: Get Closing NBV (Actuals) for September 2025
- **Row**: 260 (Closing NBV)
- **Column**: P (Sep 2025)
- **Cell**: P260

### Example 3: Get BB Forecast Opening GBV for Non Prime in December 2025
- **Row**: 5 (Sum of OpeningGBV, NON PRIME)
- **Column**: S (Dec 2025)
- **Cell**: S5

### Example 4: Get RAM excl. DS gain as % of revenue for July 2025
- **Row**: 308 (RAM as % of revenue)
- **Column**: N (Jul 2025)
- **Cell**: N308

---

## Python Code Snippet - Extract Specific Metric

```python
import openpyxl

# Open workbook
wb = openpyxl.load_workbook("Forecast Baseline Outputs v3.6 (new collections & impairment).xlsx", data_only=True)
ws = wb["forecast vs actuals"]

# Example: Get Total Collections (Row 200) for March 2025 (Column J)
total_collections_mar = ws['J200'].value
print(f"Total Collections March 2025: {total_collections_mar}")

# Example: Get Closing NBV (Row 260) for Sep 2025 (Column P)
closing_nbv_sep = ws['P260'].value
print(f"Closing NBV September 2025: {closing_nbv_sep}")

# Example: Loop through all months for Total Collections
from openpyxl.utils import get_column_letter

# Columns H to Q = Jan 2025 to Oct 2025
for col_num in range(8, 18):  # H=8, Q=17
    col_letter = get_column_letter(col_num)
    value = ws[f'{col_letter}200'].value
    month_date = ws[f'{col_letter}1'].value
    print(f"{month_date}: {value}")

wb.close()
```

---

## Top 10 Key Metrics (Most Commonly Used)

| # | Metric | Row | Section |
|---|--------|-----|---------|
| 1 | **Total Collections (P+I)** | 200 | Actuals |
| 2 | **Total Collections inc Contra** | 222 | Actuals |
| 3 | **Closing GBV** | 240 | Actuals |
| 4 | **Average GBV** | 250 | Actuals |
| 5 | **Closing NBV** | 260 | Actuals |
| 6 | **Average NBV** | 270 | Actuals |
| 7 | **Revenue** | 280 | Actuals |
| 8 | **Gross Impairment** | 291 | Actuals |
| 9 | **Net Impairment** | 339 | Actuals |
| 10 | **RAM (incl. DS gain)** | 355 | Actuals |

---

**Generated**: 2026-02-10
**For**: Jack Hipson
**Purpose**: Quick lookup for extracting metrics from forecast vs actuals sheet
