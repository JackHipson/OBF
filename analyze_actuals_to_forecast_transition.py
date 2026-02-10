"""
Analyze the ACTUAL transition from actuals to forecast in the BB model
Using the 1_Actuals_Data and 6_Combined_View sheets
"""

import pandas as pd
import numpy as np

file_path = "/home/user/OBF/Forecast Baseline Outputs v3.6 (new collections & impairment).xlsx"

print("=" * 100)
print("BB MODEL: ACTUALS → FORECAST TRANSITION ANALYSIS (COMPLETE)")
print("=" * 100)
print()

# ============================================================================
# PART 1: Read 1_Actuals_Data Sheet
# ============================================================================
print("PART 1: ACTUALS DATA (Sheet: 1_Actuals_Data)")
print("-" * 100)

try:
    df_actuals = pd.read_excel(file_path, sheet_name="1_Actuals_Data")

    print(f"Shape: {df_actuals.shape[0]} rows x {df_actuals.shape[1]} columns")
    print()
    print("Columns:")
    for i, col in enumerate(df_actuals.columns):
        print(f"  {i}: {col}")
    print()

    # Check date range
    date_cols = [col for col in df_actuals.columns if 'month' in str(col).lower() or 'date' in str(col).lower()]
    if date_cols:
        date_col = date_cols[0]
        df_actuals[date_col] = pd.to_datetime(df_actuals[date_col], errors='coerce')
        print(f"Date range: {df_actuals[date_col].min()} to {df_actuals[date_col].max()}")
        print()

    print("First 20 rows:")
    print(df_actuals.head(20).to_string())
    print()

except Exception as e:
    print(f"Error reading 1_Actuals_Data: {e}")
    df_actuals = None

# ============================================================================
# PART 2: Read 6_Combined_View Sheet
# ============================================================================
print()
print("=" * 100)
print("PART 2: COMBINED VIEW (Sheet: 6_Combined_View)")
print("=" * 100)
print()

try:
    df_combined = pd.read_excel(file_path, sheet_name="6_Combined_View")

    print(f"Shape: {df_combined.shape[0]} rows x {df_combined.shape[1]} columns")
    print()
    print("Columns:")
    for i, col in enumerate(df_combined.columns):
        print(f"  {i}: {col}")
    print()

    # Check date range
    date_cols_comb = [col for col in df_combined.columns if 'month' in str(col).lower() or 'date' in str(col).lower()]
    if date_cols_comb:
        date_col_comb = date_cols_comb[0]
        df_combined[date_col_comb] = pd.to_datetime(df_combined[date_col_comb], errors='coerce')
        print(f"Date range: {df_combined[date_col_comb].min()} to {df_combined[date_col_comb].max()}")
        print()

        # Count actuals vs forecast
        if 'Actual' in df_combined.columns or 'Type' in df_combined.columns or 'Period_Type' in df_combined.columns:
            type_col = [col for col in df_combined.columns if 'type' in str(col).lower() or 'actual' in str(col).lower()][0]
            print(f"Period breakdown (column: {type_col}):")
            print(df_combined[type_col].value_counts())
            print()

    print("First 30 rows:")
    print(df_combined.head(30).to_string())
    print()

    # ============================================================================
    # PART 3: Extract Transition Period from Combined View
    # ============================================================================
    print()
    print("=" * 100)
    print("PART 3: TRANSITION PERIOD ANALYSIS (Jul-Dec 2025)")
    print("=" * 100)
    print()

    if date_cols_comb:
        # Filter for Jul-Dec 2025
        mask = (df_combined[date_col_comb] >= '2025-07-01') & (df_combined[date_col_comb] <= '2025-12-31')
        df_transition = df_combined[mask].copy()

        if len(df_transition) > 0:
            df_transition['Month'] = df_transition[date_col_comb].dt.strftime('%Y-%m (%b)')

            # Identify metrics
            value_cols = [col for col in df_combined.columns if col not in ['Month', date_col_comb] +
                         [c for c in df_combined.columns if 'segment' in str(c).lower() or 'type' in str(c).lower() or 'cohort' in str(c).lower()]]

            print(f"Found {len(df_transition)} rows in transition period")
            print(f"Value columns to analyze: {len(value_cols)}")
            print()

            # Group by month and aggregate
            groupby_cols = ['Month']

            # Check if there's a segment column
            segment_cols = [col for col in df_transition.columns if 'segment' in str(col).lower()]

            if segment_cols:
                print(f"Data includes segment breakdown: {segment_cols[0]}")
                print(f"Segments: {df_transition[segment_cols[0]].unique()}")
                print()
                print("Aggregating ALL segments together for monthly totals...")
                print()

            # Define key metrics to track
            key_metrics = {
                'OpeningGBV': ['OpeningGBV', 'Opening_GBV', 'GBV_Opening'],
                'ClosingGBV': ['ClosingGBV', 'Closing_GBV', 'GBV', 'GBV_Closing'],
                'Coll_Principal': ['Coll_Principal', 'Principal_Collections', 'Collections_Principal'],
                'Coll_Interest': ['Coll_Interest', 'Interest_Collections', 'Collections_Interest'],
                'InterestRevenue': ['InterestRevenue', 'Interest_Revenue', 'Revenue'],
                'Net_Impairment': ['Net_Impairment', 'Impairment', 'Gross_Impairment_ExcludingDS'],
                'Provision_Balance': ['Total_Provision_Balance', 'Provision_Balance', 'Provision'],
                'Coverage_Ratio': ['Total_Coverage_Ratio', 'Coverage_Ratio', 'Coverage'],
                'ClosingNBV': ['ClosingNBV', 'Closing_NBV', 'NBV']
            }

            # Find matching columns
            metric_map = {}
            for metric_name, possible_cols in key_metrics.items():
                for col in possible_cols:
                    if col in df_transition.columns:
                        metric_map[metric_name] = col
                        break

            print("Mapped metrics:")
            for metric, col in metric_map.items():
                print(f"  {metric:20s}: {col}")
            print()

            # Aggregate by month
            monthly_totals = df_transition.groupby('Month').agg({
                col: 'sum' if 'Ratio' not in col and 'Coverage' not in col else 'mean'
                for col in metric_map.values()
            }).reset_index()

            # Sort by date
            monthly_totals = monthly_totals.sort_values('Month')

            print("=" * 100)
            print("MONTHLY SUMMARY: JUL 2025 - DEC 2025")
            print("=" * 100)
            print()

            for idx, row in monthly_totals.iterrows():
                month = row['Month']
                month_num = int(month.split('-')[1].split()[0])
                period_type = "*** ACTUAL ***" if month_num <= 9 else "*** FORECAST ***"

                print(f"{month} {period_type}")
                print("-" * 100)

                for metric_name, col in metric_map.items():
                    value = row[col]

                    if 'Ratio' in metric_name or 'Coverage' in metric_name:
                        print(f"  {metric_name:25s}: {value:10.2%}")
                    else:
                        print(f"  {metric_name:25s}: £{value/1_000_000:12.2f}m")

                print()

            # ============================================================================
            # PART 4: CRITICAL TRANSITION ANALYSIS (Sep → Oct)
            # ============================================================================
            print()
            print("=" * 100)
            print("*** CRITICAL TRANSITION: SEP 2025 (ACTUAL) → OCT 2025 (FORECAST) ***")
            print("=" * 100)
            print()

            sep_data = monthly_totals[monthly_totals['Month'].str.contains('2025-09')]
            oct_data = monthly_totals[monthly_totals['Month'].str.contains('2025-10')]

            if len(sep_data) > 0 and len(oct_data) > 0:
                print("ABSOLUTE VALUES:")
                print("-" * 100)
                print(f"{'Metric':<25s} {'Sep 2025':>15s} {'Oct 2025':>15s} {'Change':>15s} {'% Change':>12s}")
                print("-" * 100)

                for metric_name, col in metric_map.items():
                    sep_val = sep_data[col].iloc[0]
                    oct_val = oct_data[col].iloc[0]
                    change = oct_val - sep_val

                    if 'Ratio' in metric_name or 'Coverage' in metric_name:
                        pct_change = (change / sep_val * 100) if sep_val != 0 else 0
                        change_bps = change * 10000
                        print(f"{metric_name:<25s} {sep_val:>14.2%} {oct_val:>14.2%} {change_bps:>13.0f}bp {pct_change:>11.1f}%")
                    else:
                        pct_change = (change / abs(sep_val) * 100) if sep_val != 0 else 0
                        print(f"{metric_name:<25s} £{sep_val/1_000_000:>13.2f}m £{oct_val/1_000_000:>13.2f}m £{change/1_000_000:>12.2f}m {pct_change:>11.1f}%")

                print()
                print()
                print("KEY OBSERVATIONS:")
                print("-" * 100)

                # Check for significant jumps
                gbv_change = (oct_data[metric_map['ClosingGBV']].iloc[0] - sep_data[metric_map['ClosingGBV']].iloc[0]) / sep_data[metric_map['ClosingGBV']].iloc[0] * 100
                if abs(gbv_change) > 5:
                    print(f"  WARNING: Large GBV change of {gbv_change:+.1f}% from Sep to Oct")
                    print(f"           This suggests a discontinuity in the forecast starting point")

                if 'Coverage_Ratio' in metric_map:
                    cov_change = (oct_data[metric_map['Coverage_Ratio']].iloc[0] - sep_data[metric_map['Coverage_Ratio']].iloc[0]) * 10000
                    if abs(cov_change) > 200:
                        print(f"  WARNING: Large coverage ratio jump of {cov_change:+.0f} bps from Sep to Oct")
                        print(f"           Check if methodology changed between actuals and forecast")

                if 'Net_Impairment' in metric_map:
                    imp_sep = sep_data[metric_map['Net_Impairment']].iloc[0]
                    imp_oct = oct_data[metric_map['Net_Impairment']].iloc[0]
                    imp_change_pct = ((imp_oct - imp_sep) / abs(imp_sep) * 100) if imp_sep != 0 else 0
                    if abs(imp_change_pct) > 50:
                        print(f"  WARNING: Large impairment change of {imp_change_pct:+.1f}% from Sep to Oct")
                        print(f"           Sep: £{imp_sep/1_000_000:.2f}m → Oct: £{imp_oct/1_000_000:.2f}m")

                print()
            else:
                print("WARNING: Could not find Sep or Oct data in the combined view")
                print(f"Sep data rows: {len(sep_data)}")
                print(f"Oct data rows: {len(oct_data)}")
                print()
        else:
            print("No data found for Jul-Dec 2025 period")

except Exception as e:
    print(f"Error reading 6_Combined_View: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# PART 5: Read forecast vs actuals Sheet
# ============================================================================
print()
print("=" * 100)
print("PART 5: FORECAST VS ACTUALS COMPARISON (Sheet: forecast vs actuals)")
print("=" * 100)
print()

try:
    df_vs = pd.read_excel(file_path, sheet_name="forecast vs actuals")

    print(f"Shape: {df_vs.shape[0]} rows x {df_vs.shape[1]} columns")
    print()
    print("Columns:")
    for i, col in enumerate(df_vs.columns):
        print(f"  {i}: {col}")
    print()
    print("First 30 rows:")
    print(df_vs.head(30).to_string())
    print()

except Exception as e:
    print(f"Error reading 'forecast vs actuals': {e}")

print()
print("=" * 100)
print("ANALYSIS COMPLETE")
print("=" * 100)
