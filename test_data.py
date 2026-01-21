import pandas as pd

# Test loading the CSV
try:
    df = pd.read_csv('sample_data/west_bengal_road_tenders_sample.csv')
    print("✅ CSV loaded successfully!")
    print(f"Total rows: {len(df)}")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nFirst 3 rows:")
    print(df.head(3))
    print(f"\nData types:")
    print(df.dtypes)
    print(f"\nYears available: {sorted(df['Award_Year'].unique())}")
    print(f"Districts: {sorted(df['District'].unique())}")
    print(f"Departments: {sorted(df['Department'].unique())}")
except Exception as e:
    print(f"❌ Error: {e}")
