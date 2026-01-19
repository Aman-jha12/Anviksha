"""
Inflation Adjustment Module

Adjusts contract values using Indian CPI (Consumer Price Index) data.
Base year: 2024
"""

import pandas as pd
from typing import Dict


# Indian CPI data (Consumer Price Index - Base 2012=100)
# Source: Reserve Bank of India / Ministry of Statistics
# Approximate values - in production, fetch from official API
CPI_DATA: Dict[int, float] = {
    2018: 140.2,
    2019: 150.0,
    2020: 153.8,
    2021: 167.3,
    2022: 176.7,
    2023: 183.9,
    2024: 190.0  # Estimated base year
}

BASE_YEAR = 2024


def get_cpi(year: int) -> float:
    """
    Get CPI value for a given year.
    
    Args:
        year: Year (integer)
        
    Returns:
        CPI value for the year, or interpolated value if year not in data
    """
    if year in CPI_DATA:
        return CPI_DATA[year]
    
    # Interpolate for missing years
    years = sorted(CPI_DATA.keys())
    if year < min(years):
        return CPI_DATA[min(years)]
    if year > max(years):
        return CPI_DATA[max(years)]
    
    # Linear interpolation
    prev_year = max([y for y in years if y < year])
    next_year = min([y for y in years if y > year])
    
    prev_cpi = CPI_DATA[prev_year]
    next_cpi = CPI_DATA[next_year]
    
    return prev_cpi + (next_cpi - prev_cpi) * (year - prev_year) / (next_year - prev_year)


def adjust_for_inflation(value: float, contract_year: int, base_year: int = BASE_YEAR) -> float:
    """
    Adjust a monetary value for inflation.
    
    Formula: Adjusted_Value = Original_Value × (CPI_base_year / CPI_contract_year)
    
    Args:
        value: Original monetary value
        contract_year: Year when the contract was awarded
        base_year: Base year for adjustment (default: 2024)
        
    Returns:
        Inflation-adjusted value
    """
    if pd.isna(value) or pd.isna(contract_year):
        return value
    
    contract_cpi = get_cpi(int(contract_year))
    base_cpi = get_cpi(base_year)
    
    if contract_cpi == 0:
        return value
    
    adjusted_value = value * (base_cpi / contract_cpi)
    return adjusted_value


def apply_inflation_adjustment(df: pd.DataFrame, value_column: str, year_column: str, 
                               base_year: int = BASE_YEAR) -> pd.DataFrame:
    """
    Apply inflation adjustment to a DataFrame column.
    
    Args:
        df: DataFrame containing contract data
        value_column: Name of the column containing monetary values
        year_column: Name of the column containing year information
        base_year: Base year for adjustment
        
    Returns:
        DataFrame with new 'inflation_adjusted_value' column
    """
    df = df.copy()
    
    # Ensure year is extracted if it's a datetime
    if pd.api.types.is_datetime64_any_dtype(df[year_column]):
        df['_year'] = df[year_column].dt.year
    else:
        df['_year'] = pd.to_numeric(df[year_column], errors='coerce')
    
    # Apply inflation adjustment
    df['inflation_adjusted_value'] = df.apply(
        lambda row: adjust_for_inflation(row[value_column], row['_year'], base_year),
        axis=1
    )
    
    # Drop temporary column
    df = df.drop(columns=['_year'])
    
    return df


def get_inflation_adjustment_info() -> str:
    """
    Get a plain English explanation of the inflation adjustment methodology.
    
    Returns:
        Explanation string
    """
    return (
        f"Inflation adjustment converts all contract values to {BASE_YEAR} prices using "
        f"India's Consumer Price Index (CPI). This allows fair comparison of contracts "
        f"across different years. A contract awarded in 2018 would have its value increased "
        f"to reflect {BASE_YEAR} purchasing power, making it comparable to more recent contracts."
    )
