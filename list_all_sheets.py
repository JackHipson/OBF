"""
List all sheets in the BB model file to find actuals data
"""

import pandas as pd

file_path = "/home/user/OBF/Forecast Baseline Outputs v3.6 (new collections & impairment).xlsx"

print("=" * 100)
print("ALL SHEETS IN WORKBOOK")
print("=" * 100)
print()

# Get all sheet names
xl_file = pd.ExcelFile(file_path)
sheet_names = xl_file.sheet_names

print(f"Total sheets: {len(sheet_names)}")
print()

for i, sheet_name in enumerate(sheet_names, 1):
    print(f"{i:2d}. {sheet_name}")

print()
print("=" * 100)
print("RECOMMENDED NEXT STEPS:")
print("=" * 100)
print()
print("This forecast output file starts from Oct 2025.")
print()
print("To analyze the actuals → forecast transition, you need to:")
print()
print("1. Find the ACTUALS file that contains Jan-Sep 2025 data")
print("   - Look for files like 'Actuals Output', 'Historical Data', or similar")
print("   - The actuals file should have the same structure (9_Summary, 11_Impairment sheets)")
print()
print("2. OR check if the model has a combined output that includes both:")
print("   - Look in the directory for other Excel files")
print("   - The combined file might have 'Full' or 'Complete' in the name")
print()
print("3. Then compare:")
print("   - Sep 2025 (last actual month) from the actuals file")
print("   - Oct 2025 (first forecast month) from this forecast file")
