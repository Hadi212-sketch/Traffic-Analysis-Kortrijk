"""
Script to regenerate df_model.csv from the notebook data
Run this if you encounter parquet corruption issues
"""
import pandas as pd
import os

print("Regenerating model data file...")

# Try to load from existing parquet (if readable)
try:
    print("Attempting to read existing parquet with different engine...")
    df = pd.read_parquet("models/df_model.parquet", engine='fastparquet')
    print("✓ Successfully read parquet with fastparquet")
except Exception as e1:
    try:
        df = pd.read_parquet("models/df_model.parquet", engine='pyarrow')
        print("✓ Successfully read parquet with pyarrow")
    except Exception as e2:
        print(f"✗ Parquet file is corrupted: {e2}")
        print("\nYou need to re-run the notebook cells to regenerate the data.")
        print("Open notebooks/RandomForestRegressor.ipynb and run all cells,")
        print("especially the cell with df_model.to_parquet() or df_model.to_csv()")
        exit(1)

# Save as CSV (more reliable)
csv_path = "models/df_model.csv"
print(f"Saving to {csv_path}...")
df.to_csv(csv_path, index=False)
print(f"✓ Successfully saved {len(df)} rows to CSV")

# Try to save as parquet with different settings
try:
    print("Attempting to save as parquet with different compression...")
    df.to_parquet("models/df_model.parquet", engine='pyarrow', compression='snappy')
    print("✓ Successfully saved parquet file")
except Exception as e:
    print(f"✗ Could not save parquet: {e}")
    print("CSV file is available as fallback")

print("\n✅ Done! You can now run the Streamlit app.")
