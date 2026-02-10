"""
Check the actual date range in the BB model file
"""

import pandas as pd

file_path = "/home/user/OBF/Forecast Baseline Outputs v3.6 (new collections & impairment).xlsx"

print("=" * 100)
print("DATE RANGE CHECK")
print("=" * 100)
print()

# Check 9_Summary
print("9_SUMMARY SHEET:")
print("-" * 100)
df_summary = pd.read_excel(file_path, sheet_name="9_Summary")
df_summary['ForecastMonth'] = pd.to_datetime(df_summary['ForecastMonth'], errors='coerce')

print(f"Earliest date: {df_summary['ForecastMonth'].min()}")
print(f"Latest date: {df_summary['ForecastMonth'].max()}")
print(f"Total unique months: {df_summary['ForecastMonth'].nunique()}")
print()
print("All unique months:")
unique_months = sorted(df_summary['ForecastMonth'].dropna().unique())
for month in unique_months:
    month_str = pd.to_datetime(month).strftime('%Y-%m (%b)')
    count = len(df_summary[df_summary['ForecastMonth'] == month])
    print(f"  {month_str}: {count} rows")

print()
print()

# Check 11_Impairment
print("11_IMPAIRMENT SHEET:")
print("-" * 100)
df_imp = pd.read_excel(file_path, sheet_name="11_Impairment")
df_imp['ForecastMonth'] = pd.to_datetime(df_imp['ForecastMonth'], errors='coerce')

print(f"Earliest date: {df_imp['ForecastMonth'].min()}")
print(f"Latest date: {df_imp['ForecastMonth'].max()}")
print(f"Total unique months: {df_imp['ForecastMonth'].nunique()}")
print()
print("All unique months:")
unique_months_imp = sorted(df_imp['ForecastMonth'].dropna().unique())
for month in unique_months_imp:
    month_str = pd.to_datetime(month).strftime('%Y-%m (%b)')
    count = len(df_imp[df_imp['ForecastMonth'] == month])
    print(f"  {month_str}: {count} rows")

print()
print("=" * 100)
print("CONCLUSION:")
print("=" * 100)
print()
if df_summary['ForecastMonth'].min() >= pd.to_datetime('2025-10-01'):
    print("WARNING: This file contains FORECAST data only (Oct 2025+)")
    print("It does NOT contain actuals for Jul-Sep 2025.")
    print()
    print("To analyze the actuals → forecast transition, you need:")
    print("  1. A file with actual data for Jul-Sep 2025, OR")
    print("  2. A different sheet in this workbook that contains actuals")
else:
    print("This file contains both actuals and forecast data.")
