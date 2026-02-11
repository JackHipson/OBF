# Backbook Loan Portfolio Forecast - Build Prompt

> **Instructions**: Copy the text below (between the START/END markers) and paste it as your prompt in a new Claude Code session. Attach `Fact_Raw_New.xlsx` to the session's working directory before sending.

---

## START OF PROMPT

I have a consumer lending portfolio and I need you to build a **monthly backbook (BB) forecast** of the P&L and balance sheet from **October 2025 to January 2029** (40 months). The attached file `Fact_Raw_New.xlsx` contains all the historical actuals you need.

ULTRATHINK and take your time. This is a complex financial modelling task - accuracy matters more than speed.

---

### 1. UNDERSTANDING THE DATA

**File**: `Fact_Raw_New.xlsx` (single sheet called "result", ~105,540 rows, 24 columns)

**Dimension columns** (group-by keys):
| Column | Description | Example Values |
|--------|-------------|----------------|
| `cohort` | Origination month of the loan (YYYYMM format, plus "Pre-2020" bucket) | `202001`, `202305`, `Pre-2020` |
| `calendarmonth` | Reporting month (YYYYMM integer) | `201601` to `202509` |
| `lob` | Line of business | `Non Prime`, `Near Prime`, `Prime` |
| `loansize` | Loan size band | `£0-£5k`, `£5k-£10k`, `£10K-£15k`, `£15-£20k` |
| `onbsoffbs` | Balance sheet classification (all "On Balance Sheet") | `On Balance Sheet` |
| `dqbucket` | Days-past-due bucket (0-22) | `0`, `1`, `5`, `22` |
| `istopuploan` | Whether the loan is a top-up | `0`, `1` |
| `isdebtconsolidationloan` | Whether it's a debt consolidation loan | `0`, `1` |

**Metric columns** (numeric values):
| Column | Description | Sign Convention |
|--------|-------------|-----------------|
| `openinggbv` | Opening Gross Book Value | Positive |
| `closinggbv` | Closing Gross Book Value | Positive |
| `principalcollections` | Principal repayments collected | **Negative** (cash in) |
| `interestcollections` | Interest payments collected | **Negative** (cash in) |
| `principalcontrasettlement` | Principal contra from top-up settlements | Typically negative |
| `nonprincipalcontrasettlement` | Non-principal contra settlements | Typically negative |
| `debtsalewriteoffs` | Write-offs from quarterly debt sales | Positive = loss |
| `otherwriteoffs` | Other write-offs (credit losses) | Positive = loss |
| `interestrevenue` | Interest revenue accrued (P&L) | Positive |
| `disbursalsexcltopup` | New loan disbursals (excl top-ups) | Positive |
| `disbursalstopup` | Top-up disbursals | Positive |
| `loanamount` | Total loan amount | Positive |
| `intramonthprovision` | Intra-month provision movement (may contain "null" strings for early periods) | Signed |
| `intramonthprovision2` | Second provision movement field (may contain "null" strings) | Signed |
| `provisionatmonthend` | Provision balance at month-end (IFRS 9/IAS 39 impairment reserve) | Positive |
| `debtsaleproceeds` | Cash received from debt sales (may contain "null" strings) | Positive |

**IMPORTANT data quirks you must handle**:
- The `cohort` field includes a `"Pre-2020"` bucket for older loans - treat this as a single synthetic cohort
- Some columns contain the string `"null"` instead of NaN/None in early periods - convert these to 0 or NaN as appropriate
- There is **no explicit MOB (Months on Book) column** - you must calculate it: `MOB = calendarmonth - cohort` (in months). For "Pre-2020", assume cohort = 201601 (or earliest calendarmonth in the data) for MOB calculation
- `principalcollections` and `interestcollections` are **negative** numbers (cash inflows)
- Data runs from Jan 2016 to Sep 2025 (~9.5 years of history)
- There are 69 unique cohorts (monthly from Jan 2020 to Sep 2025, plus Pre-2020)
- LOB has 3 values: `Non Prime`, `Near Prime`, `Prime`

---

### 2. WHAT IS A "BACKBOOK" FORECAST?

- **Backbook (BB)**: All loans originated **before** the cutoff date (October 2025). These loans already exist and are running off (amortising) over time.
- **Frontbook (FB)**: Loans originated **from** October 2025 onwards. These are future originations that we are NOT forecasting here.
- The actuals data contains the **total book** (BB + FB combined). To isolate the backbook, filter to cohorts with origination month < 202510 (i.e., all loans issued before October 2025).
- Since all cohorts in the data are <= 202509, the entire dataset IS the backbook for an Oct 2025 cutoff. No new loans are added from Oct 2025 onwards - the book purely runs off.

---

### 3. METRICS TO FORECAST (monthly, Oct 2025 - Jan 2029)

For each forecast month, produce these metrics (aggregated across all BB cohorts):

| # | Metric | Definition |
|---|--------|------------|
| 1 | **Opening GBV** | Gross Book Value at start of month (= prior month Closing GBV) |
| 2 | **Principal Collections** | Cash collected as principal repayments (negative = inflow) |
| 3 | **Interest Collections** | Cash collected as interest payments (negative = inflow) |
| 4 | **Contra Settlements (Principal)** | GBV reduction from top-up loan settlements |
| 5 | **Contra Settlements (Non-Principal)** | Non-principal contra adjustments |
| 6 | **Debt Sale Write-offs** | GBV written off through quarterly debt sales (Mar, Jun, Sep, Dec only) |
| 7 | **Other Write-offs** | Non-debt-sale credit write-offs |
| 8 | **Closing GBV** | = Opening GBV - |Principal Collections| - |Interest Collections| - Contras - Write-offs + Interest Revenue |
| 9 | **Interest Revenue** | P&L interest income accrual |
| 10 | **Provision Balance** | IFRS 9 / IAS 39 impairment provision at month-end |
| 11 | **Gross Impairment (excl. Debt Sale)** | = -(Non-DS Provision Movement) + Other Write-offs |
| 12 | **Net Impairment** | = Gross Impairment + Debt Sale Impact |
| 13 | **Closing NBV** | = Closing GBV - Provision Balance |

---

### 4. HOW TO BUILD THE FORECAST

Follow this general approach. You have discretion to improve on it, but this is the proven architecture:

#### Step 1: Data Preparation
- Read the Excel file, clean "null" strings, ensure numeric types
- Calculate MOB for each row: `MOB = (calendarmonth_year - cohort_year) * 12 + (calendarmonth_month - cohort_month)`
- Decide on segmentation. The existing model uses 5 segments by mapping `lob` × `loansize`:
  - **NON PRIME**: `lob == "Non Prime"` (all loan sizes combined)
  - **NRP-S** (Near Prime Small): `lob == "Near Prime"` AND `loansize == "£0-£5k"`
  - **NRP-M** (Near Prime Medium): `lob == "Near Prime"` AND `loansize in ["£5k-£10k"]`
  - **NRP-L** (Near Prime Large): `lob == "Near Prime"` AND `loansize in ["£10K-£15k", "£15-£20k"]`
  - **PRIME**: `lob == "Prime"` (all loan sizes combined)

  You may choose a different segmentation if you believe it produces better results, but document your choice.
- Aggregate data to the level of: **Segment × Cohort × CalendarMonth (→ MOB)**
- Calculate **rates** as % of Opening GBV for each metric at each Segment × Cohort × MOB intersection

#### Step 2: Rate Curve Construction
For each metric, build a forecast rate for every Segment × Cohort × future MOB. Recommended approaches (in order of preference):

1. **Cohort Average (CohortAvg)**: Average the rate at a given MOB across the last N cohorts that have reached that MOB. Good for mature, stable metrics.
2. **Cohort Trend (CohortTrend)**: Fit a linear regression to the rate vs MOB for a specific cohort, then extrapolate. Good for metrics with clear trends (like coverage ratio which rises with MOB).
3. **Donor Cohort**: For young cohorts that haven't reached high MOBs yet, borrow the rate curve from a more mature "donor" cohort and apply it. Good for collections/revenue on recently originated cohorts.
4. **Segment Median**: Take the median rate across all cohorts in a segment at each MOB. Useful for volatile metrics like write-offs.

**Key insight from previous modelling**: The **Coverage Ratio (Provision / GBV)** is the most critical and hardest metric to get right. It drives the entire impairment forecast because:
- `Provision Balance = Closing GBV × Coverage Ratio`
- `Provision Movement = Provision[t] - Provision[t-1]`
- `Gross Impairment ≈ -Provision Movement + Write-offs`

If the coverage ratio trajectory is wrong, everything downstream is wrong. Pay special attention to:
- Coverage ratios typically **increase with MOB** (older loans have higher provisions)
- The rate of increase varies significantly by segment (Non Prime rises faster than Prime)
- Using CohortTrend for CR can produce trajectories that are **too flat** for Non Prime, leading to underestimated impairment
- A good approach: use **DonorCohort** or **CohortAvg** for coverage ratios on Non Prime (borrow from mature cohorts that show the full lifecycle), and **CohortTrend** for Near Prime segments

#### Step 3: Seed the Forecast
- The **seed** (starting point) is the last actual month: **September 2025** (calendarmonth = 202509)
- For each Segment × Cohort, extract from Sep 2025 actuals:
  - Closing GBV → becomes Oct 2025 Opening GBV
  - Provision at Month End → becomes the prior provision for Oct 2025
  - MOB at Sep 2025 → Oct MOB = Sep MOB + 1

#### Step 4: Run the Forecast Engine (month by month)
For each forecast month (Oct 2025, Nov 2025, ..., Jan 2029):
1. Look up the forecast rate for each metric at the current Segment × Cohort × MOB
2. Apply rates to Opening GBV to get absolute amounts
3. Calculate Closing GBV using the GBV waterfall
4. Calculate Provision Balance = Closing GBV × Coverage Ratio
5. Calculate impairment from provision movement
6. The Closing GBV and Provision become the seed for the next month
7. Increment MOB by 1

#### Step 5: Debt Sale Mechanics
Debt sales occur quarterly in **March, June, September, and December**:
- **Debt Sale Write-offs**: GBV written off (apply WO_DebtSold rate only in these months, zero in others)
- **DS Provision Release**: When GBV is written off, the associated provision is released = DS_Coverage_Ratio × DS_WriteOffs (use ~78.5%)
- **DS Proceeds**: Cash received from selling the debt = DS_Proceeds_Rate × DS_WriteOffs (use ~24p per £1)
- **Debt Sale Impact** = -WriteOffs + Provision Release + Proceeds (net P&L impact, usually a small gain or loss)

In non-debt-sale months, set all DS-related amounts to zero.

#### Step 6: Impairment Calculation
The full impairment waterfall is:
```
Total Provision Balance     = Closing GBV × Coverage Ratio
Total Provision Movement    = Provision[t] - Provision[t-1]
DS Provision Release        = DS_Coverage_Ratio × DS_WriteOffs  (quarterly months only)
Non-DS Provision Movement   = Total Provision Movement + DS Provision Release
Gross Impairment (excl DS)  = -(Non-DS Provision Movement) + (-Other Write-offs)
Debt Sale Impact            = (-DS WriteOffs) + DS Provision Release + DS Proceeds
Net Impairment              = Gross Impairment (excl DS) + Debt Sale Impact
Closing NBV                 = Closing GBV - Total Provision Balance
```

Sign convention for P&L reporting:
- Impairment charges (bad) = **negative**
- Impairment releases/gains (good) = **positive**
- Write-offs = **negative** (expense)
- Collections = **negative** in the raw data (cash inflow)

---

### 5. OUTPUT REQUIREMENTS

Produce the following outputs:

1. **Monthly Summary Table** (Oct 2025 - Jan 2029): All 13 metrics listed above, aggregated across segments, one row per month. Export to Excel.

2. **Segment-Level Detail**: Same metrics broken down by the 5 segments (or whatever segmentation you chose).

3. **Cohort-Level Detail**: Full granular output showing Segment × Cohort × Month with all rates and amounts. Export to Excel/CSV.

4. **Transparency Report**: For each forecast rate used, show what approach was used (CohortAvg, DonorCohort, etc.) and the underlying data that produced it.

---

### 6. TESTING AND VALIDATION

Once you have built the forecast, validate it thoroughly:

#### Test A: Forward Test (Oct 2025 onwards)
- The actual data goes up to Sep 2025, but the "total book" actuals for Oct 2025 onwards exist in reality. Since I only have actuals to Sep 2025, compare:
  - Check that **Oct 2025 Opening GBV** from your forecast matches **Sep 2025 Closing GBV** from actuals exactly (this should be automatic)
  - Check that forecast metrics for Oct 2025 are in a sensible range compared to the Sep 2025 actuals (no sudden jumps or discontinuities at the transition point)
  - Flag any metric that changes by more than 20% month-on-month at the actuals-to-forecast boundary

#### Test B: Retrospective Backtest
- Shift the cutoff date backwards:
  - **Cutoff = July 2025**: Use data up to Jun 2025 as inputs, forecast Jul-Sep 2025, compare forecast to actual Jul-Sep 2025
  - **Cutoff = April 2025**: Use data up to Mar 2025 as inputs, forecast Apr-Sep 2025, compare forecast to actual Apr-Sep 2025
- For each backtest:
  - Calculate the variance (forecast - actual) for each metric in absolute terms and as % of GBV
  - Identify which segments and cohorts drive the largest variances
  - If backtest variances are consistently large, revise your methodology before producing the final Oct 2025 forecast

#### Test C: Reasonableness Checks
- **GBV should decline monotonically** (no new loans in BB, so the book only runs off)
- **Coverage ratio should generally increase with time** (older loans = higher provisions)
- **Collections as % of GBV should be roughly stable or slowly declining** (book quality shouldn't change dramatically)
- **Interest revenue as % of GBV should be stable** (interest rate embedded in existing loans doesn't change)
- **Provision balance should increase initially** (CR increasing faster than GBV declining) then eventually decrease (GBV declining faster than CR can grow)
- **No metric should suddenly spike or crash** at the actuals-to-forecast boundary

---

### 7. VARIANCE ANALYSIS

After completing the forecast and backtesting:
1. Document the **top 5 largest variances** between your backtest forecast and actuals
2. For each variance, explain:
   - Which segment/cohort drives it
   - What the root cause is (methodology limitation, data anomaly, structural change)
   - Whether the variance is **systematic** (persists across backtests) or **idiosyncratic** (one-off)
3. Explain what assumptions are baked into your forecast that could cause variance vs actual outcomes:
   - e.g., "I assume collection rates stay flat at recent averages, but if the macro environment worsens, actual collections could fall short"
   - e.g., "Debt sales are modelled quarterly with fixed 78.5% coverage and 24p proceeds rate - actual sales may differ"

---

### 8. DELIVERABLES CHECKLIST

Please produce:
- [ ] Python script(s) that read the Excel file, build the forecast, and output results
- [ ] Monthly summary Excel output (all metrics, Oct 2025 - Jan 2029)
- [ ] Segment-level detail Excel output
- [ ] Backtest results (at least 2 cutoff points)
- [ ] Variance analysis write-up (markdown or text)
- [ ] Documentation of methodology choices and any assumptions made
- [ ] A summary of key findings and confidence level in the forecast

ULTRATHINK!

## END OF PROMPT
