import pandas as pd
import numpy as np
from pathlib import Path

# File paths
file_requested = '/home/user/OBF/forecast_output/Forecast_Transparency_Report.xlsx'
file_newest = '/home/user/OBF/output_v32_27m/Forecast_Transparency_Report.xlsx'

def extract_monthly_totals(file_path):
    """Extract monthly totals for key metrics"""

    print(f"\n{'='*100}")
    print(f"FILE: {Path(file_path).parent.name}/{Path(file_path).name}")
    print(f"{'='*100}\n")

    if not Path(file_path).exists():
        print(f"FILE NOT FOUND")
        return

    # Read the forecast output sheet
    try:
        df = pd.read_excel(file_path, sheet_name='5_Forecast_Output')
        print(f"Forecast Output Sheet: {df.shape[0]} rows x {df.shape[1]} columns\n")
    except Exception as e:
        print(f"Error reading Forecast Output: {e}")
        return

    # Check for summary sheet
    try:
        summary_df = pd.read_excel(file_path, sheet_name='9_Summary')
        print(f"\n{'='*100}")
        print("SUMMARY SHEET FOUND")
        print(f"{'='*100}\n")
        print(f"Shape: {summary_df.shape[0]} rows x {summary_df.shape[1]} columns")
        print("\nFirst 30 rows:")
        print(summary_df.head(30).to_string(index=False))

        # Check if there are budget columns
        budget_cols = [col for col in summary_df.columns if 'budget' in str(col).lower()]
        if budget_cols:
            print(f"\n\nBUDGET COLUMNS FOUND: {budget_cols}")

    except Exception as e:
        print(f"\nNo Summary sheet or error reading: {e}")

    # Extract monthly aggregates from forecast output
    print(f"\n\n{'='*100}")
    print("MONTHLY TOTALS FROM FORECAST OUTPUT")
    print(f"{'='*100}\n")

    # Group by forecast month
    monthly = df.groupby('ForecastMonth').agg({
        'Coll_Principal': 'sum',
        'Coll_Interest': 'sum',
        'InterestRevenue': 'sum',
        'ClosingGBV': 'sum',
        'ClosingNBV': 'sum',
        'Gross_Impairment_ExcludingDS': 'sum',
        'Net_Impairment': 'sum'
    }).reset_index()

    # Calculate total collections and coverage ratio
    monthly['Total_Collections'] = monthly['Coll_Principal'] + monthly['Coll_Interest']
    monthly['Coverage_Ratio'] = (monthly['ClosingGBV'] - monthly['ClosingNBV']) / monthly['ClosingGBV']

    # Format for display
    monthly['ForecastMonth'] = pd.to_datetime(monthly['ForecastMonth']).dt.strftime('%Y-%m')

    # Display key metrics
    print("MONTHLY TOTALS:")
    print("-" * 100)

    metrics_display = monthly[[
        'ForecastMonth',
        'Total_Collections',
        'InterestRevenue',
        'Gross_Impairment_ExcludingDS',
        'ClosingGBV',
        'ClosingNBV',
        'Coverage_Ratio'
    ]].copy()

    # Format numbers
    for col in ['Total_Collections', 'InterestRevenue', 'Gross_Impairment_ExcludingDS',
                'ClosingGBV', 'ClosingNBV']:
        metrics_display[col] = metrics_display[col].apply(lambda x: f"{x:,.0f}")

    metrics_display['Coverage_Ratio'] = metrics_display['Coverage_Ratio'].apply(lambda x: f"{x:.2%}")

    print(metrics_display.to_string(index=False))

    # Check for Details sheet with budget comparison
    print(f"\n\n{'='*100}")
    print("CHECKING DETAILS SHEET FOR BUDGET COMPARISON")
    print(f"{'='*100}\n")

    try:
        details_df = pd.read_excel(file_path, sheet_name='10_Details')
        print(f"Details Sheet: {details_df.shape[0]} rows x {details_df.shape[1]} columns")
        print("\nFirst 25 rows:")
        print(details_df.head(25).to_string(index=False))

        # Check for budget-related columns
        budget_cols = [col for col in details_df.columns if any(keyword in str(col).lower()
                      for keyword in ['budget', 'variance', 'delta', 'vs', 'comparison'])]
        if budget_cols:
            print(f"\n\nBUDGET-RELATED COLUMNS: {budget_cols}")

    except Exception as e:
        print(f"No Details sheet or error: {e}")

# Analyze both files
print("\n" + "="*100)
print("EXTRACTING MONTHLY TOTALS AND FORECAST VS BUDGET")
print("="*100)

extract_monthly_totals(file_requested)
print("\n\n")
extract_monthly_totals(file_newest)

print("\n" + "="*100)
print("EXTRACTION COMPLETE")
print("="*100)
