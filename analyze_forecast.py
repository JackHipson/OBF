import pandas as pd
import openpyxl
from pathlib import Path

# File paths
file_requested = '/home/user/OBF/forecast_output/Forecast_Transparency_Report.xlsx'
file_newest = '/home/user/OBF/output_v32_27m/Forecast_Transparency_Report.xlsx'

def analyze_excel_file(file_path):
    """Analyze Excel file structure and extract key data"""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {file_path}")
    print(f"{'='*80}\n")

    # Check if file exists
    if not Path(file_path).exists():
        print(f"FILE NOT FOUND: {file_path}")
        return

    # 1. List all sheets
    try:
        xl_file = pd.ExcelFile(file_path)
        sheets = xl_file.sheet_names
        print(f"SHEETS FOUND ({len(sheets)}):")
        for i, sheet in enumerate(sheets, 1):
            print(f"  {i}. {sheet}")
        print()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # 2. Look for forecast vs budget comparison sheets
    comparison_sheets = [s for s in sheets if any(keyword in s.lower() for keyword in
                        ['forecast', 'budget', 'comparison', 'vs', 'variance'])]

    if comparison_sheets:
        print(f"\nFORECAST/BUDGET COMPARISON SHEETS:")
        for sheet in comparison_sheets:
            print(f"  - {sheet}")
            try:
                df = pd.read_excel(file_path, sheet_name=sheet)
                print(f"    Shape: {df.shape[0]} rows x {df.shape[1]} columns")
                print(f"    Preview:")
                print(df.head(10).to_string(index=False))
                print()
            except Exception as e:
                print(f"    Error reading sheet: {e}\n")

    # 3. Extract monthly totals for specific metrics
    print(f"\n{'='*80}")
    print("SEARCHING FOR KEY METRICS")
    print(f"{'='*80}\n")

    metrics_to_find = [
        'Collections', 'Interest Revenue', 'Gross Impairment',
        'Closing GBV', 'Closing NBV', 'Coverage Ratio'
    ]

    for sheet in sheets:
        try:
            df = pd.read_excel(file_path, sheet_name=sheet)

            # Check if any metric names appear in the first column or as row headers
            if df.shape[0] > 0 and df.shape[1] > 0:
                first_col = df.iloc[:, 0].astype(str)

                found_metrics = []
                for metric in metrics_to_find:
                    # Check if metric appears anywhere in first column
                    matches = first_col[first_col.str.contains(metric, case=False, na=False)]
                    if len(matches) > 0:
                        found_metrics.append(metric)

                if found_metrics:
                    print(f"Sheet: '{sheet}' - Found metrics: {', '.join(found_metrics)}")
                    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
                    print(f"\nFirst few rows:")
                    print(df.head(15).to_string(index=False))
                    print("\n" + "-"*80 + "\n")

        except Exception as e:
            pass  # Skip sheets that can't be read

    # 4. Look for rate curve sheets
    print(f"\n{'='*80}")
    print("RATE CURVE SHEETS")
    print(f"{'='*80}\n")

    rate_sheets = [s for s in sheets if any(keyword in s.lower() for keyword in
                  ['rate', 'curve', 'yield', 'coverage'])]

    if rate_sheets:
        for sheet in rate_sheets:
            print(f"Sheet: '{sheet}'")
            try:
                df = pd.read_excel(file_path, sheet_name=sheet)
                print(f"  Shape: {df.shape[0]} rows x {df.shape[1]} columns")
                print(f"  Preview:")
                print(df.head(10).to_string(index=False))
                print()
            except Exception as e:
                print(f"  Error reading sheet: {e}\n")
    else:
        print("No rate curve sheets found")

# Analyze both files
print("\n" + "="*80)
print("FORECAST TRANSPARENCY REPORT ANALYSIS")
print("="*80)

analyze_excel_file(file_requested)
analyze_excel_file(file_newest)

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
