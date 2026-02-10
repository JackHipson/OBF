# "forecast vs actuals" Sheet Structure - Complete Map

## File
`/home/user/OBF/Forecast Baseline Outputs v3.6 (new collections & impairment).xlsx`

## Sheet Dimensions
- **Total rows**: 682
- **Total columns**: 70 (A through BR)

---

## Overall Structure - 4 Main Sections

### 1. BB FORECAST (Detailed) - Rows 1-48
**Purpose**: Back Book forecast data broken down by metric and segment

**Key Columns**:
- **Column O**: Metric names (e.g., "Sum of OpeningGBV", "Sum of Coll_Principal")
- **Column P**: Segment names (NON PRIME, NRP-L, NRP-M, NRP-S, PRIME)
- **Columns Q → BC**: Monthly forecast data starting Oct 2025

**Metrics Included** (Column O):
- Row 5: Sum of OpeningGBV
- Row 10: Sum of Coll_Principal
- Row 15: Sum of Coll_Interest
- Row 20: Sum of ClosingGBV
- Row 25: Sum of ClosingNBV
- Row 30: Sum of InterestRevenue
- Row 35: Sum of Gross_Impairment_ExcludingDS
- Row 40: Sum of Net_Impairment

Each metric has 5 rows (one per segment):
1. NON PRIME (total)
2. NRP-L (Near Prime Large)
3. NRP-M (Near Prime Medium)
4. NRP-S (Near Prime Small)
5. PRIME

---

### 2. BB FORECAST (Summary) - Rows 49-193
**Purpose**: Summarized BB forecast with percentages and ratios

**Marker**: Row 49, Column E: "FORECAST (BB Only)>>>"

**Key Columns**:
- **Column F**: Metric/segment labels
- **Columns Q → BC**: Monthly forecast data

**Sample Metrics** (Column F):
- Row 51-54: Collections by segment (Non Prime, Near Prime Small, Near Prime Medium, Prime)
- Row 55: BB coll + principal collections
- Row 56-60: as % of average closing GBV (by segment)
- Row 62-65: Segment breakdowns
- Row 66: BB Closing GBV
- Row 67-70: Segment mix percentages
- Row 72-76: Various BB metrics
- Row 107-111: Total as % of average GBV
- Row 118-127: Revenue percentages
- Row 134-143: More percentage breakdowns

---

### 3. ACTUALS (Total Book) - Rows 194-368
**Purpose**: Actual total book performance data

**Marker**: Row 194, Column E: "ACTUALS (total book)>>>"

**Key Columns**:
- **Column F**: Metric labels
- **Columns H → P (and beyond)**: Actual monthly data
  - H = Jan 2025
  - I = Feb 2025
  - J = Mar 2025
  - K = Apr 2025
  - L = May 2025
  - M = Jun 2025
  - N = Jul 2025
  - O = Aug 2025
  - P = Sep 2025
  - Q = Oct 2025
- **Column BF**: Appears to be FY26 total or summary column

**Key Metrics** (Column F):
- **Row 196-199**: Collections by segment (Non Prime, NRP Small, NRP Medium, Prime)
- **Row 200**: Principal + Interest collections (TOTAL)
- **Row 202-205**: Collections as % of average GBV (by segment)

- **Row 207-210**: Contra collections by segment
- **Row 211**: Total contra collections
- **Row 213-216**: Contra as % of average GBV

- **Row 218-221**: Total collections inc contra (by segment)
- **Row 222**: Total collections inc contra (TOTAL)
- **Row 224-227**: Total collections as % of average GBV

- **Row 240**: Closing GBV
- **Row 241-244**: Segment mix percentages

- **Row 246-249**: Average GBV by segment
- **Row 250**: Average GBV (TOTAL)

- **Row 260**: Closing NBV
- **Row 270**: Average NBV

- **Row 280**: Revenue (TOTAL)
- **Row 281**: Total as % of average GBV

- **Row 291**: Total Gross impairment
- **Row 292**: as % of revenue
- **Row 297**: as % of average GBV

- **Row 307**: RAM (excl. debt sale gain)
- **Row 308**: as % of revenue
- **Row 313**: as % of average GBV

- **Row 323**: Debt Sale Gain
- **Row 324**: as % gross impairment
- **Row 329**: as % of average GBV

- **Row 339**: Net impairment
- **Row 340**: as % gross impairment
- **Row 345**: as % of average GBV

- **Row 355**: RAM (incl. debt sale gain)
- **Row 356**: as % of revenue
- **Row 361**: as % of average GBV

---

### 4. VARIANCES (Forecast vs Actuals) - Rows 369-682
**Purpose**: Calculated variances between BB forecast and total book actuals

**Marker**: Row 369, Column E: "VARIANCES (forecast minus actuals)>>>"

**Key Columns**:
- **Column F**: Metric labels (mirrors the structure of forecast/actuals sections)
- **Data columns**: Variance calculations (Forecast - Actuals)

**Sample Metrics** (Column F):
- Row 372-375: Collections variances by segment
- Row 376: BB total collections variance
- Row 377-381: % of average closing GBV variances
- Row 383-387: Additional variances
- Row 388+: Segment mix and other variance metrics

---

## Month Header Mapping

### Row 1 (Main headers - for ACTUALS section)
```
Column H = 2025-01-31 (Jan 2025)
Column I = 2025-02-28 (Feb 2025)
Column J = 2025-03-31 (Mar 2025)
Column K = 2025-04-30 (Apr 2025)
Column L = 2025-05-31 (May 2025)
Column M = 2025-06-30 (Jun 2025)
Column N = 2025-07-31 (Jul 2025)
Column O = 2025-08-31 (Aug 2025)
Column P = 2025-09-30 (Sep 2025)
Column Q = 2025-10-31 (Oct 2025)
Column R = 2025-11-30 (Nov 2025)
Column S = 2025-12-31 (Dec 2025)
Column T = 2026-01-31 (Jan 2026)
...continues through to Column BC and beyond
```

### Row 4 (Forecast section headers)
```
Column O = Values (label column)
Column P = Segment (label column)
Column Q = 2025-10-31 (Oct 2025) - FIRST forecast month
Column R = 2025-11-30 (Nov 2025)
Column S = 2025-12-31 (Dec 2025)
...continues
```

**Note**: The FORECAST section starts from Column Q (Oct 2025), while ACTUALS section starts from Column H (Jan 2025). This means actuals cover Jan-Sep 2025, and forecast covers Oct 2025 onwards.

---

## Key Column Purposes

| Column | Purpose |
|--------|---------|
| E | Section markers (contains ">>>") |
| F | Primary metric/segment labels for actuals and variance sections |
| O | Metric names for BB Forecast detailed section; also Aug 2025 actuals data |
| P | Segment names for BB Forecast detailed section; also Sep 2025 actuals data |
| H-Q | Monthly data (H=Jan 2025, Q=Oct 2025) |
| BF (58) | Summary/total column (appears to be FY26 or cumulative) |

---

## Segment Names

The data is broken down by these loan segments:

1. **NON PRIME** - Total non-prime segment
   - **NRP-L** - Near Prime Large
   - **NRP-M** - Near Prime Medium
   - **NRP-S** - Near Prime Small
2. **PRIME** - Prime segment

---

## Data Extraction Tips

### To get BB Forecast data:
- **Detailed metrics**: Rows 5-44, Column O (metric name), Column P (segment), Columns Q→ (monthly data)
- **Summary metrics**: Rows 51-193, Column F (label), Columns Q→ (monthly data)

### To get Total Book Actuals data:
- **All metrics**: Rows 196-368, Column F (metric label), Columns H-P (Jan-Sep 2025 actuals)
- **Key row numbers**: See "Key Metrics" list in Section 3 above

### To get Variances:
- **All variances**: Rows 372-682, Column F (metric label), data columns show (Forecast - Actuals)

### To extract specific metric for a month:
1. Find the metric row number using Column F or Column O
2. Find the month column (e.g., Column H = Jan 2025, Column Q = Oct 2025)
3. Read the intersection

---

## Important Notes

1. **Overlapping columns**: Columns O and P serve dual purposes:
   - In forecast section (rows 1-48): Label columns (metric and segment names)
   - In actuals section (rows 194+): Data columns (Aug 2025 and Sep 2025)

2. **Date alignment**:
   - BB Forecast data starts from Oct 2025 (Column Q)
   - Actuals data starts from Jan 2025 (Column H)
   - This creates a forecast vs actuals comparison period from Oct 2025 onwards

3. **Percentage rows**: Many metrics are followed by percentage calculations (as % of revenue, as % of average GBV, etc.)

4. **Column BF**: This column appears throughout with summary values - likely FY26 totals or a specific period aggregate

---

## Scripts Created

Three Python scripts have been created to analyze this sheet:

1. **`/home/user/OBF/parse_fva_sheet.py`** - Dumps all cell values for rows 1-100
2. **`/home/user/OBF/analyze_fva_structure.py`** - Identifies section markers and key rows
3. **`/home/user/OBF/examine_actuals_section.py`** - Detailed examination of actuals section
4. **`/home/user/OBF/complete_sheet_structure.py`** - Complete structure mapping

All scripts use `openpyxl` to read the raw Excel data.

---

**Generated**: 2026-02-10
**Source File**: Forecast Baseline Outputs v3.6 (new collections & impairment).xlsx
**Sheet**: forecast vs actuals
