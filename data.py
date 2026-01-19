"""
Data Loading and Preprocessing Module

Loads the preloaded West Bengal road construction dataset.
"""

import pandas as pd
from typing import Dict, List

# Preloaded dataset - representative subset of publicly available data
PRELOADED_DATA = """Tender_ID,State,District,Department,Road_Type,Project_Length_km,Vendor_Name,Tender_Value_Cr,Award_Year,Bidders_Count
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
    Load the preloaded dataset.
    
    Returns:
        DataFrame with tender data
    """
    from io import StringIO
    df = pd.read_csv(StringIO(PRELOADED_DATA))
    
    # Convert Tender_Value_Cr to absolute value in rupees
    df['Tender_Value_Rs'] = df['Tender_Value_Cr'] * 1_00_00_000  # Convert crores to rupees
    
    # Standardize vendor names
    df['Vendor_Name'] = df['Vendor_Name'].str.strip()
    
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
