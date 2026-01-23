"""
Analysis Module

Statistical analysis and pattern detection.
Uses neutral, research-grade language.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats


def calculate_statistics(df: pd.DataFrame) -> Dict:
    """
    Calculate high-level statistics.
    
    Returns:
        Dictionary with summary statistics
    """
    if len(df) == 0:
        return {
            'total_spending': 0,
            'total_projects': 0,
            'avg_cost_per_km': 0,
            'time_range': 'N/A',
            'districts_count': 0,
            'vendors_count': 0
        }
    
    total_spending = df['Tender_Value_Adjusted_Rs'].sum()
    total_projects = len(df)
    
    # Calculate average cost per km - ENSURE we use capital L
    if 'Project_Length_km' in df.columns:
        total_length = df['Project_Length_km'].sum()
        avg_cost_per_km = (total_spending / total_length) if total_length > 0 else 0
        print(f"📊 STATS DEBUG: total_spending={total_spending:,.0f}, total_length={total_length:.2f}, avg_cost_per_km={avg_cost_per_km:,.0f}")
    else:
        print(f"❌ ERROR: Project_Length_km NOT FOUND in dataframe!")
        print(f"   Available columns: {df.columns.tolist()}")
        avg_cost_per_km = 0
    
    # Time range
    min_year = int(df['Award_Year'].min())
    max_year = int(df['Award_Year'].max())
    time_range = f"{min_year}-{max_year}" if min_year != max_year else str(min_year)
    
    return {
        'total_spending': total_spending,
        'total_projects': total_projects,
        'avg_cost_per_km': avg_cost_per_km,  # Now in rupees per km, template will convert to lakhs
        'time_range': time_range,
        'districts_count': df['District'].nunique(),
        'vendors_count': df['Vendor_Name'].nunique()
    }


def spending_by_district(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate total spending by district."""
    return df.groupby('District').agg({
        'Tender_Value_Adjusted_Rs': 'sum',
        'Tender_ID': 'count'
    }).rename(columns={
        'Tender_Value_Adjusted_Rs': 'Total_Spending',
        'Tender_ID': 'Project_Count'
    }).reset_index()


def spending_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate total spending by year."""
    return df.groupby('Award_Year').agg({
        'Tender_Value_Adjusted_Rs': 'sum',
        'Tender_ID': 'count'
    }).rename(columns={
        'Tender_Value_Adjusted_Rs': 'Total_Spending',
        'Tender_ID': 'Project_Count'
    }).reset_index()


def vendor_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze vendor patterns.
    
    Returns:
        DataFrame with vendor statistics
    """
    vendor_stats = df.groupby('Vendor_Name').agg({
        'Tender_Value_Adjusted_Rs': ['sum', 'count', 'mean'],
        'Bidders_Count': 'mean'
    }).reset_index()
    
    vendor_stats.columns = ['Vendor_Name', 'Total_Value', 'Contract_Count', 'Avg_Value', 'Avg_Bidders']
    
    # Calculate concentration share
    total_value = df['Tender_Value_Adjusted_Rs'].sum()
    vendor_stats['Share_Percent'] = (vendor_stats['Total_Value'] / total_value * 100) if total_value > 0 else 0
    
    # Sort by total value
    vendor_stats = vendor_stats.sort_values('Total_Value', ascending=False)
    
    return vendor_stats


def generate_insight_summary(df: pd.DataFrame, district: str = None, department: str = None) -> str:
    """
    Generate auto-formatted insight summary for the current dataset.
    
    Args:
        df: Filtered DataFrame
        district: Selected district (None = All)
        department: Selected department (None = All)
        
    Returns:
        Human-readable insight summary string
    """
    if df is None or len(df) == 0:
        return "No data available for the selected filters."
    
    try:
        # Build context
        context_parts = []
        if district and district != "All":
            context_parts.append(district)
        if department and department != "All":
            context_parts.append(department)
        
        if context_parts:
            context_str = " (" + ", ".join(context_parts) + ")"
        else:
            context_str = " across all districts"
        
        # Calculate metrics
        if 'Tender_Value_Adjusted_Rs' not in df.columns:
            return "Data not properly initialized. Please refresh the page."
        
        total_spending = df['Tender_Value_Adjusted_Rs'].sum()
        project_count = len(df)
        total_length = df['Project_Length_km'].sum()
        
        # Avoid division by zero
        if total_length > 0:
            avg_cost_per_km = total_spending / total_length
        else:
            avg_cost_per_km = 0
        
        # Year range
        if len(df) > 0 and 'Award_Year' in df.columns:
            min_year = int(df['Award_Year'].min())
            max_year = int(df['Award_Year'].max())
            year_range = f"{min_year}–{max_year}" if min_year != max_year else str(max_year)
        else:
            year_range = "N/A"
        
        # Count observations
        observations = detect_statistical_observations(df)
        high_cost_count = len([o for o in observations if o['type'] == 'high_cost'])
        low_competition_count = len([o for o in observations if o['type'] == 'low_competition'])
        
        # Build narrative with proper formatting
        narrative = (
            f"For {context_str} between {year_range}, total inflation-adjusted spending was "
            f"<strong>₹{total_spending/1_00_00_000:.2f} crore</strong> across <strong>{project_count} project(s)</strong>. "
        )
        
        if total_length > 0:
            narrative += (
                f"Average cost per km was <strong>₹{avg_cost_per_km/1_00_000:.2f} lakh</strong>. "
            )
        
        if high_cost_count > 0 or low_competition_count > 0:
            observations_text = []
            if high_cost_count > 0:
                observations_text.append(f"{high_cost_count} above-median contract value(s)")
            if low_competition_count > 0:
                observations_text.append(f"{low_competition_count} limited-bidder project(s)")
            
            narrative += (
                f"Analysis identified <strong>{' and '.join(observations_text)}</strong>. "
                "See statistical observations below for details."
            )
        else:
            narrative += "All metrics remained within expected ranges for the selected dataset."
        
        return narrative
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating insight summary: {str(e)}")
        return "Analysis summary could not be generated. Please refresh the page."


def detect_statistical_observations(df: pd.DataFrame) -> List[Dict]:
    """
    Detect notable statistical patterns with confidence indicators.
    
    Uses neutral language only.
    
    Returns:
        List of observation dictionaries with confidence scoring
    """
    observations = []
    
    if len(df) == 0:
        return observations
    
    # 1. HIGH-COST OUTLIERS
    median_value = df['Tender_Value_Adjusted_Rs'].median()
    q3 = df['Tender_Value_Adjusted_Rs'].quantile(0.75)
    q1 = df['Tender_Value_Adjusted_Rs'].quantile(0.25)
    iqr = q3 - q1
    outlier_threshold = q3 + 1.5 * iqr
    
    high_cost = df[df['Tender_Value_Adjusted_Rs'] > outlier_threshold]
    
    for _, row in high_cost.iterrows():
        ratio = row['Tender_Value_Adjusted_Rs'] / median_value if median_value > 0 else 1
        percentile = (df['Tender_Value_Adjusted_Rs'] <= row['Tender_Value_Adjusted_Rs']).sum() / len(df) * 100
        
        observations.append({
            'type': 'high_cost',
            'tender_id': row['Tender_ID'],
            'title': 'Statistical Pattern: Above-Median Contract Value',
            'description': (
                f"Tender {row['Tender_ID']} has an inflation-adjusted value of "
                f"₹{row['Tender_Value_Adjusted_Rs']/1_00_00_000:.2f} crore, which is "
                f"{ratio:.1f}× the median value (₹{median_value/1_00_00_000:.2f} Cr). "
                f"This places it in the {percentile:.0f}th percentile of contract values."
            ),
            'confidence': 'High',
            'confidence_reason': 'Statistical deviation detected via IQR method (>Q3 + 1.5×IQR)',
            'does_not_imply': 'Irregularity, wrongdoing, or cost overrun. May reflect project complexity, scope, or market conditions.',
            'value': row['Tender_Value_Adjusted_Rs'],
            'year': row['Award_Year']
        })
    
    # 2. LOW BIDDER COUNT + HIGH VALUE
    low_bidder_threshold = 3
    high_value_threshold = df['Tender_Value_Adjusted_Rs'].quantile(0.75)
    
    low_competition = df[
        (df['Bidders_Count'] <= low_bidder_threshold) & 
        (df['Tender_Value_Adjusted_Rs'] > high_value_threshold)
    ]
    
    median_bidders = df['Bidders_Count'].median()
    
    for _, row in low_competition.iterrows():
        bidder_percentile = (df['Bidders_Count'] <= row['Bidders_Count']).sum() / len(df) * 100
        
        observations.append({
            'type': 'low_competition',
            'tender_id': row['Tender_ID'],
            'title': 'Observable Pattern: Limited Bidder Participation',
            'description': (
                f"Tender {row['Tender_ID']} received {int(row['Bidders_Count'])} bidder(s) "
                f"(compared to a median of {median_bidders:.0f} bidders). "
                f"The contract value of ₹{row['Tender_Value_Adjusted_Rs']/1_00_00_000:.2f} crore is in the "
                f"top quartile. Limited bidding may reflect project-specific constraints or market factors."
            ),
            'confidence': 'Medium',
            'confidence_reason': 'Rule-based detection: bidders ≤3 AND value ≥75th percentile',
            'does_not_imply': 'Restricted bidding or improper procurement. May indicate specialized requirements or limited vendor availability.',
            'value': row['Tender_Value_Adjusted_Rs'],
            'year': row['Award_Year'],
            'bidders': int(row['Bidders_Count'])
        })
    
    # 3. YEAR-OVER-YEAR INCREASES
    vendor_district = df.groupby(['Vendor_Name', 'District', 'Award_Year']).agg({
        'Tender_Value_Adjusted_Rs': 'mean',
        'Tender_ID': 'first'
    }).reset_index()
    
    vendor_district = vendor_district.sort_values(['Vendor_Name', 'District', 'Award_Year'])
    
    for vendor in vendor_district['Vendor_Name'].unique():
        vendor_data = vendor_district[vendor_district['Vendor_Name'] == vendor]
        for district in vendor_data['District'].unique():
            district_data = vendor_data[vendor_data['District'] == district].sort_values('Award_Year')
            if len(district_data) >= 2:
                values = district_data['Tender_Value_Adjusted_Rs'].values
                years = district_data['Award_Year'].values
                
                for i in range(1, len(values)):
                    if values[i] > values[i-1] * 1.5:  # 50% increase
                        increase_pct = ((values[i] - values[i-1]) / values[i-1]) * 100
                        
                        observations.append({
                            'type': 'year_over_year',
                            'tender_id': f"{vendor} - {district}",
                            'title': 'Statistical Observation: Year-over-Year Value Change',
                            'description': (
                                f"Contracts awarded to {vendor} in {district} increased by "
                                f"{increase_pct:.0f}% from {years[i-1]} to {years[i]} "
                                f"(₹{values[i-1]/1_00_00_000:.2f}Cr → ₹{values[i]/1_00_00_000:.2f}Cr). "
                                f"This may reflect changes in project scope, complexity, inflation, or material costs."
                            ),
                            'confidence': 'Low',
                            'confidence_reason': 'Observed change without causal context; requires domain knowledge to interpret.',
                            'does_not_imply': 'Improper pricing or escalation. Increases are common due to inflation and project variation.',
                            'value': values[i],
                            'year': years[i]
                        })
    
    # Add safe defaults so UI never shows blank fields
    DEFAULTS = {
        'confidence': 'Medium',
        'confidence_reason': 'Descriptive statistical rule (percentile/IQR) applied.',
        'does_not_imply': 'Irregularity or wrongdoing. Patterns are descriptive and may reflect scope or market factors.'
    }
    for o in observations:
        o.setdefault('confidence', DEFAULTS['confidence'])
        o.setdefault('confidence_reason', DEFAULTS['confidence_reason'])
        o.setdefault('does_not_imply', DEFAULTS['does_not_imply'])

    return observations


def calculate_cost_per_km(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate cost per km for each project."""
    df = df.copy()
    df['Cost_Per_Km'] = df['Tender_Value_Adjusted_Rs'] / df['Project_Length_km']
    return df


def run_comprehensive_analysis(df: pd.DataFrame, z_threshold: float = 2.5) -> dict:
    """
    Run comprehensive analysis on procurement data.
    
    Args:
        df: Processed DataFrame with procurement data
        z_threshold: Z-score threshold for anomaly detection (default 2.5)
    
    Returns:
        Dictionary containing analysis results and flagged tenders
    """
    
    # Calculate summary statistics
    summary_stats = {
        'total_tenders': len(df),
        'median_value': df['inflation_adjusted_value'].median() if 'inflation_adjusted_value' in df.columns else 0,
        'mean_value': df['inflation_adjusted_value'].mean() if 'inflation_adjusted_value' in df.columns else 0,
        'unique_vendors': df['vendor_name'].nunique() if 'vendor_name' in df.columns else 0,
    }
    
    # Initialize flag columns
    df['is_price_anomaly'] = False
    df['is_vendor_dominance'] = False
    df['is_low_competition'] = False
    df['z_score'] = np.nan
    df['ratio_to_median'] = np.nan
    df['vendor_contract_count'] = 0
    
    # 1. PRICE ANOMALY DETECTION
    if 'inflation_adjusted_value' in df.columns:
        values = df['inflation_adjusted_value'].dropna()
        if len(values) > 0:
            mean_val = values.mean()
            std_val = values.std()
            
            if std_val > 0:
                df['z_score'] = (df['inflation_adjusted_value'] - mean_val) / std_val
                df['is_price_anomaly'] = df['z_score'].abs() > z_threshold
            
            median_val = values.median()
            if median_val > 0:
                df['ratio_to_median'] = df['inflation_adjusted_value'] / median_val
    
    # 2. VENDOR DOMINANCE DETECTION
    if 'vendor_name' in df.columns:
        vendor_counts = df['vendor_name'].value_counts()
        df['vendor_contract_count'] = df['vendor_name'].map(vendor_counts)
        
        # Vendor dominance: vendor has >30% of contracts or significantly more than average
        avg_contracts = len(df) / len(vendor_counts) if len(vendor_counts) > 0 else 0
        df['is_vendor_dominance'] = (df['vendor_contract_count'] > avg_contracts * 2) | \
                                     (df['vendor_contract_count'] / len(df) > 0.3)
    
    # 3. LOW COMPETITION DETECTION
    if 'num_bidders' in df.columns:
        median_bidders = df['num_bidders'].median()
        df['is_low_competition'] = df['num_bidders'] < (median_bidders * 0.5) if median_bidders > 0 else False
    
    # Flag tenders with any anomaly
    df['is_flagged'] = df['is_price_anomaly'] | df['is_vendor_dominance'] | df['is_low_competition']
    flagged_tenders = df[df['is_flagged']].copy()
    
    # Count anomalies
    summary_stats['price_anomalies'] = df['is_price_anomaly'].sum()
    summary_stats['vendor_dominance'] = df['is_vendor_dominance'].sum()
    summary_stats['low_competition'] = df['is_low_competition'].sum()
    summary_stats['flagged_tenders'] = len(flagged_tenders)
    
    return {
        'flagged_tenders': flagged_tenders,
        'summary_stats': summary_stats,
        'full_data': df
    }
