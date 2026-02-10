import pandas as pd
from pathlib import Path

# File paths
file_requested = '/home/user/OBF/forecast_output/Forecast_Transparency_Report.xlsx'
file_newest = '/home/user/OBF/output_v32_27m/Forecast_Transparency_Report.xlsx'

def check_budget_sheets(file_path):
    """Check specific sheets for budget comparison data"""

    print(f"\n{'='*100}")
    print(f"FILE: {Path(file_path).parent.name}/{Path(file_path).name}")
    print(f"{'='*100}\n")

    if not Path(file_path).exists():
        print(f"FILE NOT FOUND")
        return

    # Check Reconciliation sheet
    try:
        print("=" * 100)
        print("RECONCILIATION SHEET")
        print("=" * 100)
        recon_df = pd.read_excel(file_path, sheet_name='12_Reconciliation')
        print(f"\nShape: {recon_df.shape[0]} rows x {recon_df.shape[1]} columns")
        print(f"\nColumns: {list(recon_df.columns)}")
        print(f"\nFirst 30 rows:")
        print(recon_df.head(30).to_string(index=False))
    except Exception as e:
        print(f"Error reading Reconciliation: {e}")

    # Check Validation sheet
    try:
        print(f"\n\n{'=' * 100}")
        print("VALIDATION SHEET")
        print("=" * 100)
        val_df = pd.read_excel(file_path, sheet_name='13_Validation')
        print(f"\nShape: {val_df.shape[0]} rows x {val_df.shape[1]} columns")
        print(f"\nColumns: {list(val_df.columns)}")
        print(f"\nFirst 30 rows:")
        print(val_df.head(30).to_string(index=False))
    except Exception as e:
        print(f"Error reading Validation: {e}")

    # Check README sheet for context
    try:
        print(f"\n\n{'=' * 100}")
        print("README SHEET")
        print("=" * 100)
        readme_df = pd.read_excel(file_path, sheet_name='README')
        print(f"\nShape: {readme_df.shape[0]} rows x {readme_df.shape[1]} columns")
        print(f"\nContent:")
        print(readme_df.to_string(index=False))
    except Exception as e:
        print(f"Error reading README: {e}")

# Check both files
print("\n" + "="*100)
print("CHECKING BUDGET COMPARISON SHEETS")
print("="*100)

check_budget_sheets(file_requested)
print("\n\n")
check_budget_sheets(file_newest)

print("\n" + "="*100)
print("CHECK COMPLETE")
print("="*100)
