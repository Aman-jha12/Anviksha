"""
Data Loading and Preprocessing Module

Loads the preloaded West Bengal road construction dataset.
"""

import pandas as pd
from typing import Dict, List
import os

# Preloaded dataset - representative subset of publicly available data
PRELOADED_DATA = """Tender_ID,State,District,Department,Road_Type,Project_length_km,Vendor_name,Tender_value_cr,Award_year,Bidders_count
WB-RD-001,West Bengal,Howrah,PWD,Rural,5.2,Shivam Infra Projects Pvt Ltd,3.9,2019,6
WB-RD-002,West Bengal,Howrah,PWD,Rural,5.0,RK Constructions India Pvt Ltd,4.2,2020,5
WB-RD-003,West Bengal,Howrah,PWD,Rural,5.1,Shivam Infra Projects Pvt Ltd,4.6,2021,5
WB-RD-004,West Bengal,Howrah,PWD,Rural,5.3,Maa Tara Builders & Co,5.0,2022,4
WB-RD-005,West Bengal,Howrah,PWD,Rural,5.0,Shivam Infra Projects Pvt Ltd,11.4,2023,2
WB-RD-006,West Bengal,Kolkata,PWD,Urban,3.8,National Roadways India Ltd,3.7,2019,7
WB-RD-007,West Bengal,Kolkata,PWD,Urban,3.9,National Roadways India Ltd,4.0,2020,6
WB-RD-008,West Bengal,Kolkata,PWD,Urban,4.1,RK Constructions India Pvt Ltd,4.3,2021,5
WB-RD-009,West Bengal,Kolkata,PWD,Urban,4.0,RK Constructions India Pvt Ltd,9.6,2023,2
WB-RD-010,West Bengal,Kolkata,PWD,Urban,3.7,Maa Tara Builders & Co,4.4,2024,5
WB-RD-011,West Bengal,Burdwan,PWD,State Highway,8.5,Pragati Highways Pvt Ltd,5.2,2019,4
WB-RD-012,West Bengal,Burdwan,PWD,State Highway,8.6,Pragati Highways Pvt Ltd,5.6,2020,4
WB-RD-013,West Bengal,Burdwan,PWD,State Highway,8.4,Pragati Highways Pvt Ltd,11.8,2023,2
WB-RD-014,West Bengal,Nadia,PWD,Rural,4.9,Bengal Infrastructure Services Ltd,4.8,2022,6
WB-RD-015,West Bengal,Nadia,PWD,Rural,5.1,Bengal Infrastructure Services Ltd,5.1,2024,6
WB-RD-016,West Bengal,Malda,PWD,Rural,6.0,Om Sai Roadworks Pvt Ltd,4.1,2019,7
WB-RD-017,West Bengal,Malda,PWD,Rural,6.1,Om Sai Roadworks Pvt Ltd,4.4,2020,6
WB-RD-018,West Bengal,Malda,PWD,Rural,6.0,Om Sai Roadworks Pvt Ltd,9.9,2023,2
WB-RD-019,West Bengal,Paschim Medinipur,PWD,Rural,5.5,Universal Infra Solutions Pvt Ltd,4.7,2021,5
WB-RD-020,West Bengal,Paschim Medinipur,PWD,Rural,5.6,Universal Infra Solutions Pvt Ltd,4.9,2024,5"""


def load_preloaded_data() -> pd.DataFrame:
    """
    Load the preloaded dataset from CSV file.
    
    Returns:
        DataFrame with tender data
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'static', 'west_bengal_road_tenders_sample.csv')
    
    # Load from CSV file
    df = pd.read_csv(csv_path)
    
    # Print original column names for debugging
    print(f"Original columns in CSV: {df.columns.tolist()}")
    
    # Only normalize column names - remove extra spaces
    df.columns = df.columns.str.strip()
    
    print(f"Cleaned columns: {df.columns.tolist()}")
    
    # Check if Tender_Value_Adjusted_Rs already exists (from your CSV)
    if 'Tender_Value_Adjusted_Rs' not in df.columns:
        # Convert Tender_Value_Cr to absolute value in rupees if needed
        if 'Tender_Value_Cr' in df.columns:
            df['Tender_Value_Rs'] = df['Tender_Value_Cr'] * 1_00_00_000
        else:
            print("Warning: No value column found in CSV")
            df['Tender_Value_Rs'] = 0
    else:
        # CSV already has adjusted values, create base column for inflation adjustment
        df['Tender_Value_Rs'] = df['Tender_Value_Adjusted_Rs']
    
    # Replace zero and null values to prevent division errors
    # MUST use EXACT column names from your CSV: Project_length_km (capital L), Bidders_count (capital C)
    numeric_columns = ['Tender_Value_Rs', 'Project_length_km', 'Bidders_count', 'Tender_Value_Adjusted_Rs']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert to numeric
            df[col] = df[col].fillna(0.01)  # Replace NaN with small value
            df[col] = df[col].replace(0, 0.01)  # Replace 0 with small value
            print(f"✓ Processed numeric column: {col}")
        else:
            print(f"⚠️ Warning: Column '{col}' not found in dataframe")
    
    # Standardize vendor names if column exists
    if 'Vendor_name' in df.columns:
        df['Vendor_name'] = df['Vendor_name'].str.strip()
        print(f"✓ Processed vendor names")
    
    print(f"Final columns available: {df.columns.tolist()}")
    print(f"Data shape: {df.shape}")
    print(f"Sample Project_length_km values: {df['Project_length_km'].head().tolist() if 'Project_length_km' in df.columns else 'NOT FOUND'}")
    
    return df


def get_filtered_data(df: pd.DataFrame, district: str = None, department: str = None) -> pd.DataFrame:
    """
    Filter data by district and/or department.
    
    Args:
        df: Full dataset
        district: District name to filter (None for all)
        department: Department name to filter (None for all)
        
    Returns:
        Filtered DataFrame
    """
    filtered = df.copy()
    
    if district and district != "All":
        filtered = filtered[filtered['District'] == district]
    
    if department and department != "All":
        filtered = filtered[filtered['Department'] == department]
    
    return filtered


def get_unique_values(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Get unique values for filters.
    
    Returns:
        Dictionary with 'districts' and 'departments' lists
    """
    return {
        'districts': ['All'] + sorted(df['District'].unique().tolist()),
        'departments': ['All'] + sorted(df['Department'].unique().tolist()),
        'road_types': ['All'] + sorted(df['Road_Type'].unique().tolist()),
        'years': sorted(df['Award_Year'].unique().tolist())
    }
