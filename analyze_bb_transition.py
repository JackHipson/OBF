"""
Analyze BB Model Transition from Actuals to Forecast
Examines the 9_Summary and 11_Impairment sheets to identify discontinuities
"""

import pandas as pd
import numpy as np
from pathlib import Path

# File path
file_path = "/home/user/OBF/Forecast Baseline Outputs v3.6 (new collections & impairment).xlsx"

print("=" * 100)
print("BB MODEL: ACTUALS → FORECAST TRANSITION ANALYSIS")
print("=" * 100)
print()

# ============================================================================
# PART 1: Read 9_Summary Sheet
# ============================================================================
print("PART 1: 9_SUMMARY SHEET STRUCTURE")
print("-" * 100)

try:
    df_summary = pd.read_excel(file_path, sheet_name="9_Summary")

    print(f"Shape: {df_summary.shape[0]} rows x {df_summary.shape[1]} columns")
    print()
    print("All Columns:")
    for i, col in enumerate(df_summary.columns):
        print(f"  {i}: {col}")
    print()
    print("First 30 rows:")
    print(df_summary.head(30).to_string())
    print()

except Exception as e:
    print(f"Error reading 9_Summary: {e}")
    df_summary = None

# ============================================================================
# PART 2: Extract Monthly Totals from 9_Summary
# ============================================================================
if df_summary is not None:
    print()
    print("=" * 100)
    print("PART 2: MONTHLY TOTALS - TRANSITION PERIOD (Jul-Dec 2025)")
    print("=" * 100)
    print()

    # Identify the date/month column (usually first column or named 'Month', 'Date', etc.)
    date_col = None
    for col in df_summary.columns:
        col_lower = str(col).lower()
        if 'month' in col_lower or 'date' in col_lower or col == df_summary.columns[0]:
            date_col = col
            break

    if date_col is None:
        date_col = df_summary.columns[0]

    print(f"Using date column: '{date_col}'")
    print()

    # Define metrics to extract
    metrics = {
        'OpeningGBV': ['OpeningGBV', 'Opening_GBV', 'Opening GBV', 'GBV_Opening'],
        'ClosingGBV': ['ClosingGBV', 'Closing_GBV', 'Closing GBV', 'GBV_Closing', 'GBV'],
        'Coll_Principal': ['Coll_Principal', 'Principal_Collections', 'Collections_Principal'],
        'Coll_Interest': ['Coll_Interest', 'Interest_Collections', 'Collections_Interest'],
        'InterestRevenue': ['InterestRevenue', 'Interest_Revenue', 'Interest Revenue', 'Revenue'],
        'Net_Impairment': ['Net_Impairment', 'Gross_Impairment_ExcludingDS', 'Impairment'],
        'Total_Provision_Balance': ['Total_Provision_Balance', 'Provision_Balance', 'Provision Balance'],
        'Total_Coverage_Ratio': ['Total_Coverage_Ratio', 'Coverage_Ratio', 'Coverage Ratio'],
        'Total_Provision_Movement': ['Total_Provision_Movement', 'Provision_Movement', 'Provision Movement']
    }

    # Find matching columns
    metric_cols = {}
    for metric_name, possible_names in metrics.items():
        for possible in possible_names:
            if possible in df_summary.columns:
                metric_cols[metric_name] = possible
                break

    print("Mapped metrics:")
    for metric, col in metric_cols.items():
        print(f"  {metric}: '{col}'")
    print()

    # Filter for Jul-Dec 2025
    df_summary[date_col] = pd.to_datetime(df_summary[date_col], errors='coerce')

    # Filter for 2025 Jul-Dec
    mask = (df_summary[date_col] >= '2025-07-01') & (df_summary[date_col] <= '2025-12-31')
    df_transition = df_summary[mask].copy()

    if len(df_transition) > 0:
        df_transition['Month'] = df_transition[date_col].dt.strftime('%Y-%m (%b)')

        # Group by month and sum (in case there are multiple segments)
        monthly_data = df_transition.groupby('Month').agg({
            **{metric_cols[k]: 'sum' for k in metric_cols.keys()}
        }).reset_index()

        print("MONTHLY AGGREGATED DATA (Jul-Dec 2025)")
        print("-" * 100)
        print()

        for idx, row in monthly_data.iterrows():
            month = row['Month']

            # Determine if actual or forecast
            # Extract month number from format like '2025-10 (Oct)'
            month_part = month.split('-')[1].split()[0]  # Get '10' from '10 (Oct)'
            month_num = int(month_part)
            period_type = "ACTUAL" if month_num <= 9 else "FORECAST"

            print(f"{month} [{period_type}]")
            print("-" * 50)

            for metric in metric_cols.keys():
                col = metric_cols[metric]
                value = row[col]

                # Format based on metric type
                if 'Ratio' in metric:
                    print(f"  {metric:30s}: {value:8.2%}")
                else:
                    print(f"  {metric:30s}: £{value/1_000_000:10.2f}m")

            print()

        # ============================================================================
        # PART 3: Month-on-Month Changes - Highlight Sep → Oct Transition
        # ============================================================================
        print()
        print("=" * 100)
        print("PART 3: MONTH-ON-MONTH CHANGES (Highlighting Sep → Oct Transition)")
        print("=" * 100)
        print()

        for i in range(1, len(monthly_data)):
            current_month = monthly_data.iloc[i]['Month']
            prev_month = monthly_data.iloc[i-1]['Month']

            # Extract month numbers from format like '2025-10 (Oct)'
            curr_month_num = int(current_month.split('-')[1].split()[0])
            prev_month_num = int(prev_month.split('-')[1].split()[0])

            # Highlight the transition
            is_transition = (prev_month_num == 9 and curr_month_num == 10)

            if is_transition:
                print("*" * 100)
                print(f"*** CRITICAL TRANSITION: {prev_month} (ACTUAL) → {current_month} (FORECAST) ***")
                print("*" * 100)
            else:
                print(f"{prev_month} → {current_month}")
                print("-" * 100)

            for metric in metric_cols.keys():
                col = metric_cols[metric]
                prev_val = monthly_data.iloc[i-1][col]
                curr_val = monthly_data.iloc[i][col]
                change = curr_val - prev_val

                # Calculate % change (avoid division by zero)
                if prev_val != 0:
                    pct_change = (change / abs(prev_val)) * 100
                else:
                    pct_change = 0.0

                # Format based on metric type
                if 'Ratio' in metric:
                    change_bps = change * 10000  # basis points
                    print(f"  {metric:30s}: {prev_val:8.2%} → {curr_val:8.2%}  ({change_bps:+8.0f} bps)")
                else:
                    print(f"  {metric:30s}: £{prev_val/1_000_000:8.2f}m → £{curr_val/1_000_000:8.2f}m  "
                          f"(£{change/1_000_000:+8.2f}m, {pct_change:+6.1f}%)")

            print()

# ============================================================================
# PART 4: Read 11_Impairment Sheet
# ============================================================================
print()
print("=" * 100)
print("PART 4: 11_IMPAIRMENT SHEET ANALYSIS")
print("=" * 100)
print()

try:
    df_impairment = pd.read_excel(file_path, sheet_name="11_Impairment")

    print(f"Shape: {df_impairment.shape[0]} rows x {df_impairment.shape[1]} columns")
    print()
    print("All Columns:")
    for i, col in enumerate(df_impairment.columns):
        print(f"  {i}: {col}")
    print()
    print("First 30 rows:")
    print(df_impairment.head(30).to_string())
    print()

    # Extract impairment metrics
    date_col_imp = None
    for col in df_impairment.columns:
        col_lower = str(col).lower()
        if 'month' in col_lower or 'date' in col_lower or col == df_impairment.columns[0]:
            date_col_imp = col
            break

    if date_col_imp is None:
        date_col_imp = df_impairment.columns[0]

    print(f"Using date column: '{date_col_imp}'")
    print()

    # Convert to datetime
    df_impairment[date_col_imp] = pd.to_datetime(df_impairment[date_col_imp], errors='coerce')

    # Filter for Jul-Dec 2025
    mask_imp = (df_impairment[date_col_imp] >= '2025-07-01') & (df_impairment[date_col_imp] <= '2025-12-31')
    df_imp_transition = df_impairment[mask_imp].copy()

    if len(df_imp_transition) > 0:
        df_imp_transition['Month'] = df_imp_transition[date_col_imp].dt.strftime('%Y-%m (%b)')

        # Identify provision and coverage columns
        prov_cols = [col for col in df_impairment.columns if 'provision' in str(col).lower() or 'balance' in str(col).lower()]
        cov_cols = [col for col in df_impairment.columns if 'coverage' in str(col).lower() or 'ratio' in str(col).lower()]
        mov_cols = [col for col in df_impairment.columns if 'movement' in str(col).lower()]

        print("IMPAIRMENT METRICS - TRANSITION PERIOD")
        print("-" * 100)
        print()

        # Group by month
        for month in df_imp_transition['Month'].unique():
            month_data = df_imp_transition[df_imp_transition['Month'] == month]

            # Extract month number from format like '2025-10 (Oct)'
            month_part = month.split('-')[1].split()[0]
            month_num = int(month_part)
            period_type = "ACTUAL" if month_num <= 9 else "FORECAST"

            print(f"{month} [{period_type}]")
            print("-" * 50)

            # Provision balance
            if prov_cols:
                for col in prov_cols[:3]:  # Limit to first 3
                    total = month_data[col].sum()
                    print(f"  {col:40s}: £{total/1_000_000:10.2f}m")

            # Coverage ratio
            if cov_cols:
                for col in cov_cols[:3]:  # Limit to first 3
                    avg = month_data[col].mean()
                    print(f"  {col:40s}: {avg:10.2%}")

            # Movement
            if mov_cols:
                for col in mov_cols[:3]:  # Limit to first 3
                    total = month_data[col].sum()
                    print(f"  {col:40s}: £{total/1_000_000:10.2f}m")

            print()

        # Comparison of Sep vs Oct
        print()
        print("=" * 100)
        print("CRITICAL COMPARISON: Sep 2025 (ACTUAL) vs Oct 2025 (FORECAST)")
        print("=" * 100)
        print()

        sep_data = df_imp_transition[df_imp_transition['Month'].str.contains('2025-09')]
        oct_data = df_imp_transition[df_imp_transition['Month'].str.contains('2025-10')]

        if len(sep_data) > 0 and len(oct_data) > 0:
            print("Provision Balance:")
            for col in prov_cols[:3]:
                sep_val = sep_data[col].sum()
                oct_val = oct_data[col].sum()
                change = oct_val - sep_val
                pct_change = (change / abs(sep_val) * 100) if sep_val != 0 else 0
                print(f"  {col:40s}: £{sep_val/1_000_000:8.2f}m → £{oct_val/1_000_000:8.2f}m "
                      f"(£{change/1_000_000:+8.2f}m, {pct_change:+6.1f}%)")
            print()

            print("Coverage Ratio:")
            for col in cov_cols[:3]:
                sep_val = sep_data[col].mean()
                oct_val = oct_data[col].mean()
                change_bps = (oct_val - sep_val) * 10000
                print(f"  {col:40s}: {sep_val:8.2%} → {oct_val:8.2%} ({change_bps:+8.0f} bps)")
            print()

            print("Provision Movement:")
            for col in mov_cols[:3]:
                sep_val = sep_data[col].sum()
                oct_val = oct_data[col].sum()
                change = oct_val - sep_val
                print(f"  {col:40s}: £{sep_val/1_000_000:8.2f}m → £{oct_val/1_000_000:8.2f}m "
                      f"(£{change/1_000_000:+8.2f}m)")
            print()

except Exception as e:
    print(f"Error reading 11_Impairment: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 100)
print("ANALYSIS COMPLETE")
print("=" * 100)
