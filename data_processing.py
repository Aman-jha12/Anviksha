"""
Data Processing Module

Handles CSV loading, cleaning, and standardization of procurement data.
"""

import pandas as pd
import numpy as np
from typing import Optional, List


def standardize_vendor_name(name: str) -> str:
    """
    Standardize vendor names by normalizing common variations.
    
    Examples:
        "ABC Pvt Ltd" -> "ABC PVT LTD"
        "XYZ Private Limited" -> "XYZ PRIVATE LIMITED"
        "Company Inc." -> "COMPANY INC"
    """
    if pd.isna(name) or name == '':
        return ''
    
    name = str(name).strip().upper()
    
    # Normalize common company suffixes
    replacements = {
        'PVT. LTD.': 'PVT LTD',
        'PVT LTD.': 'PVT LTD',
        'PRIVATE LIMITED': 'PVT LTD',
        'PRIVATE LTD.': 'PVT LTD',
        'PRIVATE LTD': 'PVT LTD',
        'LIMITED': 'LTD',
        'LTD.': 'LTD',
        'INCORPORATED': 'INC',
        'INC.': 'INC',
        ' & ': ' AND ',
        '.': '',  # Remove periods
        ',': ''   # Remove commas
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    # Remove extra spaces
    name = ' '.join(name.split())
    
    return name


def clean_numeric_column(series: pd.Series, remove_currency: bool = True) -> pd.Series:
    """
    Clean numeric column by removing currency symbols, commas, and converting to float.
    
    Args:
        series: Pandas Series with numeric/string values
        remove_currency: Whether to remove currency symbols
        
    Returns:
        Cleaned numeric Series
    """
    series = series.copy()
    
    if remove_currency:
        # Remove common currency symbols and text
        series = series.astype(str).str.replace('₹', '', regex=False)
        series = series.astype(str).str.replace('Rs.', '', regex=False)
        series = series.astype(str).str.replace('Rs', '', regex=False)
        series = series.astype(str).str.replace('INR', '', regex=False)
        series = series.astype(str).str.replace(',', '', regex=False)
        series = series.astype(str).str.replace(' ', '', regex=False)
    
    # Convert to numeric, coercing errors to NaN
    series = pd.to_numeric(series, errors='coerce')
    
    return series


def load_and_clean_csv(file_input, 
                       value_column: Optional[str] = None,
                       vendor_column: Optional[str] = None,
                       date_column: Optional[str] = None,
                       department_column: Optional[str] = None) -> pd.DataFrame:
    """
    Load CSV file and perform basic cleaning.
    
    Args:
        file_input: Path to CSV file (str) or file-like object (e.g., BytesIO from Streamlit)
        value_column: Name of column containing contract values (auto-detect if None)
        vendor_column: Name of column containing vendor names (auto-detect if None)
        date_column: Name of column containing dates (auto-detect if None)
        department_column: Name of column containing departments (auto-detect if None)
        
    Returns:
        Cleaned DataFrame
    """
    # Load CSV (handles both file paths and file-like objects)
    df = pd.read_csv(file_input)
    
    # Auto-detect columns if not provided
    value_column = value_column or _detect_column(df, ['amount', 'value', 'price', 'contract_value', 'tender_value'])
    vendor_column = vendor_column or _detect_column(df, ['vendor', 'contractor', 'bidder', 'company', 'firm'])
    date_column = date_column or _detect_column(df, ['date', 'award_date', 'tender_date', 'contract_date'])
    department_column = department_column or _detect_column(df, ['department', 'dept', 'organization', 'agency'])
    
    # Standardize column names (only rename columns that were found)
    rename_dict = {}
    if value_column:
        rename_dict[value_column] = 'contract_value'
    if vendor_column:
        rename_dict[vendor_column] = 'vendor_name'
    if date_column:
        rename_dict[date_column] = 'contract_date'
    if department_column:
        rename_dict[department_column] = 'department'
    
    df = df.rename(columns=rename_dict)
    
    # Clean contract values
    if 'contract_value' in df.columns:
        df['contract_value'] = clean_numeric_column(df['contract_value'])
    
    # Standardize vendor names
    if 'vendor_name' in df.columns:
        df['vendor_name'] = df['vendor_name'].apply(standardize_vendor_name)
    
    # Parse dates
    if 'contract_date' in df.columns:
        df['contract_date'] = pd.to_datetime(df['contract_date'], errors='coerce')
    
    # Filter for road construction (basic filtering - can be enhanced)
    if 'description' in df.columns or 'category' in df.columns:
        desc_col = 'description' if 'description' in df.columns else 'category'
        road_keywords = ['road', 'highway', 'street', 'pavement', 'bridge', 'culvert']
        mask = df[desc_col].astype(str).str.lower().str.contains('|'.join(road_keywords), na=False)
        df = df[mask].copy()
    
    # Remove rows with missing critical data
    df = df.dropna(subset=['contract_value', 'vendor_name'], how='any')
    
    # Remove rows with zero or negative values
    df = df[df['contract_value'] > 0]
    
    return df.reset_index(drop=True)


def _detect_column(df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
    """Auto-detect column name from possible options."""
    df_columns_lower = [col.lower() for col in df.columns]
    
    for name in possible_names:
        for col in df.columns:
            if name.lower() in col.lower():
                return col
    
    return None


def prepare_analysis_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare DataFrame for analysis by adding derived columns.
    
    Args:
        df: Cleaned DataFrame
        
    Returns:
        DataFrame with analysis-ready columns
    """
    df = df.copy()
    
    # Extract year from date
    if 'contract_date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['contract_date']):
        df['year'] = df['contract_date'].dt.year
    elif 'year' not in df.columns:
        df['year'] = pd.NaT
    
    # Add placeholder for number of bidders if not present
    if 'num_bidders' not in df.columns:
        df['num_bidders'] = np.nan
    
    # Ensure required columns exist
    required_cols = ['contract_value', 'vendor_name', 'department']
    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan
    
    return df
