"""
Explanations Module

Generates plain-English explanations for flagged anomalies.
"""

import pandas as pd
from typing import Dict, Optional


def explain_price_anomaly(row: pd.Series, median_value: float, mean_value: float) -> str:
    """
    Generate plain-English explanation for price anomaly.
    
    Args:
        row: DataFrame row containing tender information
        median_value: Median contract value for comparison
        mean_value: Mean contract value for comparison
        
    Returns:
        Plain English explanation string
    """
    value = row.get('inflation_adjusted_value', 0)
    ratio = row.get('ratio_to_median', 1.0)
    percentile = row.get('price_percentile', 50.0)
    z_score = row.get('z_score', 0)
    
    # Build explanation
    parts = []
    
    if ratio > 1.0:
        ratio_text = f"{ratio:.1f}×" if ratio < 10 else f"{ratio:.0f}×"
        parts.append(
            f"This contract value ({_format_currency(value)}) is {ratio_text} higher than "
            f"the inflation-adjusted median ({_format_currency(median_value)}) for similar road projects."
        )
    
    if percentile > 95:
        parts.append(
            f"The contract price falls in the {percentile:.1f}th percentile, meaning it is higher than "
            f"{100 - percentile:.1f}% of all similar contracts."
        )
    
    if abs(z_score) > 2.5:
        parts.append(
            f"The statistical Z-score of {z_score:.2f} indicates this value is significantly different "
            f"from the average contract value."
        )
    
    if not parts:
        parts.append(
            f"This contract value ({_format_currency(value)}) is unusually high compared to "
            f"historical contracts of similar nature."
        )
    
    return " ".join(parts)


def explain_vendor_dominance(row: pd.Series, total_contracts: int) -> str:
    """
    Generate plain-English explanation for vendor dominance.
    
    Args:
        row: DataFrame row containing tender information
        total_contracts: Total number of contracts in dataset
        
    Returns:
        Plain English explanation string
    """
    vendor_name = row.get('vendor_name', 'This vendor')
    contract_count = row.get('vendor_contract_count', 0)
    contract_share = row.get('vendor_contract_share', 0)
    
    parts = []
    
    parts.append(
        f"{vendor_name} has received {contract_count} out of {total_contracts} contracts "
        f"({contract_share:.1f}% of all contracts) in this dataset."
    )
    
    if contract_share > 10:
        parts.append(
            f"This represents a high concentration of contracts awarded to a single vendor, "
            f"which may warrant further review."
        )
    
    if 'vendor_dept_share' in row and pd.notna(row.get('vendor_dept_share')):
        dept_share = row['vendor_dept_share']
        if dept_share > 20:
            dept = row.get('department', 'the same department')
            parts.append(
                f"Within {dept}, this vendor accounts for {dept_share:.1f}% of all contracts."
            )
    
    return " ".join(parts)


def explain_low_competition(row: pd.Series) -> str:
    """
    Generate plain-English explanation for low competition contracts.
    
    Args:
        row: DataFrame row containing tender information
        
    Returns:
        Plain English explanation string
    """
    num_bidders = row.get('num_bidders', 0)
    value = row.get('inflation_adjusted_value', 0)
    category = row.get('competition_category', 'low competition')
    
    parts = []
    
    if pd.notna(num_bidders):
        parts.append(
            f"This tender received only {int(num_bidders)} bidder(s), indicating {category.lower()}."
        )
    else:
        parts.append("Bidder information for this tender is not available.")
    
    if value > 0:
        parts.append(
            f"The contract was awarded at {_format_currency(value)}, "
            f"which is relatively high for a tender with limited competition."
        )
    
    parts.append(
        "Research suggests that tenders with fewer bidders may result in higher contract prices."
    )
    
    return " ".join(parts)


def generate_comprehensive_explanation(row: pd.Series, context: Dict) -> str:
    """
    Generate comprehensive explanation combining all anomaly flags.
    
    Args:
        row: DataFrame row containing tender information
        context: Dictionary with context information (median_value, total_contracts, etc.)
        
    Returns:
        Complete plain-English explanation
    """
    explanations = []
    
    # Price anomaly explanation
    if row.get('is_price_anomaly', False):
        median = context.get('median_value', 0)
        mean = context.get('mean_value', 0)
        explanations.append(explain_price_anomaly(row, median, mean))
    
    # Vendor dominance explanation
    if row.get('is_vendor_dominance', False):
        total = context.get('total_contracts', 0)
        explanations.append(explain_vendor_dominance(row, total))
    
    # Low competition explanation
    if row.get('is_low_competition', False):
        explanations.append(explain_low_competition(row))
    
    # Combine explanations
    if explanations:
        full_explanation = " • ".join(explanations)
    else:
        full_explanation = "This tender has been flagged based on statistical analysis."
    
    return full_explanation


def _format_currency(value: float) -> str:
    """Format currency value for display."""
    if pd.isna(value) or value == 0:
        return "₹0"
    
    if value >= 1_00_00_000:  # >= 1 crore
        return f"₹{value / 1_00_00_000:.2f} crore"
    elif value >= 1_00_000:  # >= 1 lakh
        return f"₹{value / 1_00_000:.2f} lakh"
    else:
        return f"₹{value:,.0f}"


def get_methodology_explanation() -> str:
    """
    Get explanation of the analysis methodology.
    
    Returns:
        Plain English methodology description
    """
    return (
        "This analysis uses statistical methods to identify patterns in public procurement data:\n\n"
        "• **Price Analysis**: Compares contract values using Z-scores and interquartile range (IQR) "
        "to identify unusually high-priced contracts.\n\n"
        "• **Vendor Concentration**: Measures how contracts are distributed among vendors to identify "
        "potential concentration of awards.\n\n"
        "• **Competition Analysis**: Examines the relationship between number of bidders and final "
        "contract prices.\n\n"
        "All contract values are adjusted for inflation to ensure fair comparison across different years. "
        "Flagged tenders represent statistical anomalies that may warrant further review but do not "
        "indicate wrongdoing."
    )
