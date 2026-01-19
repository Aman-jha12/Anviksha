"""
Inflation Adjustment Module

Adjusts historical spending to 2024 CPI base year.
"""

import pandas as pd
import numpy as np

# CPI Index for West Bengal/India (2024 = 100)
# These are representative indices; actual values should come from RBI/MOSPI
CPI_INDEX = {
    2019: 80.5,
    2020: 82.3,
    2021: 85.7,
    2022: 92.1,
    2023: 97.2,
    2024: 100.0
}


def apply_inflation_adjustment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adjust historical spending values to 2024 CPI base.
    
    Args:
        df: DataFrame with 'Award_Year' and 'Tender_Value_Rs' columns
        
    Returns:
        DataFrame with added 'Tender_Value_Adjusted_Rs' column
    """
    df = df.copy()
    
    # Add adjusted value column
    df['Tender_Value_Adjusted_Rs'] = df.apply(
        lambda row: adjust_value(row['Tender_Value_Rs'], row['Award_Year']),
        axis=1
    )
    
    # Also keep adjusted value in crores
    df['Tender_Value_Adjusted_Cr'] = df['Tender_Value_Adjusted_Rs'] / 1_00_00_000
    
    return df


def adjust_value(value: float, year: int) -> float:
    """
    Adjust a value from given year to 2024 CPI base.
    
    Args:
        value: Original value in rupees
        year: Year of the original value
        
    Returns:
        Inflation-adjusted value in 2024 rupees
    """
    if year not in CPI_INDEX:
        # If year not in index, use nearest year
        year = min(CPI_INDEX.keys(), key=lambda x: abs(x - year))
    
    # Formula: Adjusted Value = Original Value × (CPI_2024 / CPI_year)
    adjusted = value * (CPI_INDEX[2024] / CPI_INDEX[year])
    
    return adjusted


def get_cpi_multiplier(year: int) -> float:
    """
    Get the inflation multiplier for a given year.
    
    Args:
        year: Year to get multiplier for
        
    Returns:
        Multiplier to convert to 2024 base
    """
    if year not in CPI_INDEX:
        year = min(CPI_INDEX.keys(), key=lambda x: abs(x - year))
    
    return CPI_INDEX[2024] / CPI_INDEX[year]


def get_cpi_info() -> dict:
    """Get CPI index information."""
    return {
        'base_year': 2024,
        'base_index': 100.0,
        'index_values': CPI_INDEX,
        'source': 'Estimated based on RBI/MOSPI inflation data'
    }
