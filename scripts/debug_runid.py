import pandas as pd
import os

# Read the processed data
try:
    df = pd.read_csv('../data/processed/unified_printing.csv')
    print("Unique run_id values in data:")
    unique_runs = df['run_id'].unique()
    print("Raw unique values:", unique_runs)
    
    # Check types
    for run in unique_runs:
        print(f"  {run} (type: {type(run).__name__})")
    
    print(f"\nTotal records: {len(df)}")
    print("\nRecord counts by run_id:")
    counts = df['run_id'].value_counts()
    for run_id, count in counts.items():
        print(f"  {run_id} ({type(run_id).__name__}): {count} records")
        
except Exception as e:
    print(f"Error reading file: {e}")