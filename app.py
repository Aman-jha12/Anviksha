"""
Anviksha - Main Streamlit Application

Analytical Examination of Public Procurement Data
A research-focused tool for analyzing road construction tenders in West Bengal, India.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Import custom modules
from data_processing import load_and_clean_csv, prepare_analysis_dataframe
from inflation import apply_inflation_adjustment, get_inflation_adjustment_info, BASE_YEAR
from analysis import run_comprehensive_analysis
from explanations import generate_comprehensive_explanation, get_methodology_explanation

# Page configuration
st.set_page_config(
    page_title="Anviksha - Procurement Data Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS - calm, minimal, research-grade
st.markdown("""
    <style>
    /* Root theme */
    :root {
        --primary-dark: #0f172a;
        --primary-light: #1e293b;
        --neutral-light: #f8fafc;
        --neutral-medium: #cbd5e1;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-tertiary: #64748b;
        --border-color: #e2e8f0;
        --card-bg: #ffffff;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* === HEADER SECTION === */
    .header-section {
        text-align: center;
        padding: 2rem 0 1rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .header-title {
        font-size: 3rem;
        font-weight: 700;
        color: var(--primary-dark);
        letter-spacing: -0.02em;
        margin: 0;
        padding: 0;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: var(--text-tertiary);
        font-weight: 400;
        margin-top: 0.5rem;
        letter-spacing: 0.01em;
    }
    
    /* === CARD COMPONENT === */
    .card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .card-title {
        font-size: 1.35rem;
        font-weight: 600;
        color: var(--primary-dark);
        margin: 0 0 0.75rem 0;
    }
    
    .card-description {
        font-size: 0.95rem;
        color: var(--text-secondary);
        margin-bottom: 1rem;
        line-height: 1.5;
    }
    
    /* === DISCLAIMER === */
    .disclaimer-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 1.25rem;
        margin: 2rem 0;
    }
    
    .disclaimer-title {
        font-weight: 600;
        color: var(--primary-dark);
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }
    
    .disclaimer-text {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 0;
    }
    
    /* === SECTION HEADERS === */
    .section-header {
        font-size: 1.6rem;
        font-weight: 600;
        color: var(--primary-dark);
        margin-top: 2.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    .section-description {
        font-size: 0.95rem;
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    
    /* === METRICS === */
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--primary-dark);
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: var(--text-tertiary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    /* === BUTTONS === */
    .stButton > button {
        background-color: var(--primary-dark);
        color: white;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        background-color: var(--primary-light);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
    }
    
    /* === TEXT ELEMENTS === */
    h1 {
        font-size: 2.2rem;
        font-weight: 600;
        color: var(--primary-dark);
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    h2 {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--primary-dark);
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        font-size: 1.2rem;
        font-weight: 500;
        color: var(--text-primary);
        margin-top: 1.25rem;
        margin-bottom: 0.75rem;
    }
    
    /* === EXPANDER === */
    .streamlit-expanderHeader {
        background-color: var(--neutral-light);
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }
    
    /* === DATAFRAME === */
    .stDataFrame {
        font-size: 0.9rem;
    }
    
    /* === INFO/SUCCESS/ERROR BOXES === */
    .stAlert {
        border-radius: 8px;
    }
    
    /* === SPACING === */
    .element-container {
        margin-bottom: 1.25rem;
    }
    
    /* === SPINNER TEXT === */
    .stSpinner > div {
        border-color: var(--primary-dark);
    }
    </style>
""", unsafe_allow_html=True)


def render_header():
    """Render centered header section."""
    st.markdown("""
    <div class="header-section">
        <h1 class="header-title">Anviksha</h1>
        <p class="header-subtitle">Analytical Examination of Public Procurement Data</p>
    </div>
    """, unsafe_allow_html=True)


def render_disclaimer():
    """Render disclaimer card."""
    st.markdown("""
    <div class="disclaimer-card">
        <div class="disclaimer-title">⚠️ Disclaimer</div>
        <p class="disclaimer-text">
        This tool highlights statistical anomalies in public procurement data to support transparency 
        and research. It does not determine intent or wrongdoing. All analysis is based on publicly 
        available data and statistical methods.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_card(title: str, description: str, content_fn=None):
    """Render a card container with optional content."""
    st.markdown(f"""
    <div class="card">
        <div class="card-title">{title}</div>
        <div class="card-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)
    if content_fn:
        content_fn()


def main():
    """Main application entry point."""
    
    # Render header
    render_header()
    
    # Render disclaimer
    render_disclaimer()
    
    # Sidebar - minimal
    with st.sidebar:
        st.markdown("### 📋 Data & Settings")
        
        uploaded_file = st.file_uploader(
            "Upload CSV file",
            type=['csv'],
            help="Upload a CSV file containing public procurement tender data"
        )
        
        # Initialize variables
        value_col = None
        vendor_col = None
        date_col = None
        dept_col = None
        z_threshold = 2.5
        
        if uploaded_file is not None:
            st.success("✓ File uploaded")
            
            with st.expander("🔧 Advanced Settings", expanded=False):
                st.markdown("**Column Mapping**")
                value_col_input = st.text_input("Value Column", value="", key="val_col")
                vendor_col_input = st.text_input("Vendor Column", value="", key="vend_col")
                date_col_input = st.text_input("Date Column", value="", key="date_col")
                dept_col_input = st.text_input("Department Column", value="", key="dept_col")
                
                value_col = value_col_input if value_col_input else None
                vendor_col = vendor_col_input if vendor_col_input else None
                date_col = date_col_input if date_col_input else None
                dept_col = dept_col_input if dept_col_input else None
                
                st.markdown("**Analysis Settings**")
                z_threshold = st.slider("Z-Score Threshold", 2.0, 4.0, 2.5, 0.1, help="Lower = more sensitive")
    
    # Main content
    if uploaded_file is None:
        show_welcome_screen()
    else:
        try:
            process_and_display_data(
                uploaded_file,
                value_col,
                vendor_col,
                date_col,
                dept_col,
                z_threshold
            )
        except Exception as e:
            st.error(f"An error occurred during processing: {str(e)}")
            with st.expander("Debug Information"):
                st.exception(e)


def show_welcome_screen():
    """Display welcome screen with instructions."""
    st.markdown("""
    <div class="section-header">Step 1: Upload Public Tender Data</div>
    <div class="section-description">
    Use the sidebar to upload a CSV file containing tender data. Anviksha will analyze pricing patterns, 
    vendor dominance, and competition signals.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Expected CSV Columns:**")
        st.markdown("""
        - Contract Value/Amount
        - Vendor Name
        - Award/Contract Date
        - Department (optional)
        - Description (for road project filtering)
        - Number of Bidders (optional)
        """)
    
    with col2:
        st.markdown("**Analysis Features:**")
        st.markdown("""
        - ✓ Inflation adjustment to 2024 prices
        - ✓ Price anomaly detection
        - ✓ Vendor concentration analysis
        - ✓ Competition analysis
        - ✓ Plain-English explanations
        """)
    
    st.markdown("---")
    
    with st.expander("📚 Methodology", expanded=False):
        methodology = get_methodology_explanation()
        st.markdown(methodology)
    
    with st.expander("💱 Inflation Adjustment", expanded=False):
        info = get_inflation_adjustment_info()
        st.markdown(f"{info}\n\nAll values are adjusted to {BASE_YEAR} prices using India's Consumer Price Index (CPI).")


def process_and_display_data(file, value_col, vendor_col, date_col, dept_col, z_threshold):
    """Process uploaded data and display results."""
    
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'processed_df' not in st.session_state:
        st.session_state.processed_df = None
    
    # === STEP 2: RUN ANALYSIS ===
    st.markdown("""
    <div class="section-header">Step 2: Run Analysis</div>
    <div class="section-description">
    This will analyze pricing patterns, vendor dominance, and competition signals in your tender data.
    </div>
    """, unsafe_allow_html=True)
    
    run_button_col = st.columns([1, 2, 1])
    with run_button_col[1]:
        run_analysis = st.button("🔍 Run Analysis", use_container_width=True, type="primary")
    
    if run_analysis:
        with st.spinner("📊 Analyzing procurement patterns…"):
            try:
                # Load and clean data
                df = load_and_clean_csv(
                    file,
                    value_column=value_col if value_col else None,
                    vendor_column=vendor_col if vendor_col else None,
                    date_column=date_col if date_col else None,
                    department_column=dept_col if dept_col else None
                )
                
                # Prepare for analysis
                df = prepare_analysis_dataframe(df)
                
                # Apply inflation adjustment
                df = apply_inflation_adjustment(df, 'contract_value', 'contract_date')
                
                # Store processed data
                st.session_state.processed_df = df
                
                # Run analysis
                results = run_comprehensive_analysis(df, z_threshold=z_threshold)
                st.session_state.analysis_results = results
                
                st.success("✓ Analysis complete!")
                
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")
                return
    
    # Display results if available
    if st.session_state.analysis_results is not None:
        display_results(st.session_state.analysis_results, st.session_state.processed_df)
    elif st.session_state.processed_df is not None:
        st.info("👆 Click 'Run Analysis' to view results")


def display_results(results: dict, df: pd.DataFrame):
    """Display analysis results in professional dashboard format."""
    
    flagged = results['flagged_tenders']
    stats = results['summary_stats']
    
    # === STEP 3: KEY SIGNALS ===
    st.markdown("""
    <div class="section-header">Step 3: Key Signals</div>
    <div class="section-description">
    High-level summary of your procurement analysis.
    </div>
    """, unsafe_allow_html=True)
    
    # Three metric cards
    metric_cols = st.columns(3)
    
    with metric_cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_tenders']:,}</div>
            <div class="metric-label">Total Tenders Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[1]:
        flagged_count = stats['flagged_tenders']
        flagged_pct = (flagged_count / stats['total_tenders'] * 100) if stats['total_tenders'] > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{flagged_count:,}</div>
            <div class="metric-label">Flagged Anomalies ({flagged_pct:.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['unique_vendors']:,}</div>
            <div class="metric-label">Vendors with High Concentration</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Anomaly breakdown
    st.markdown("""
    <div class="section-header">Anomaly Breakdown</div>
    """, unsafe_allow_html=True)
    
    breakdown_cols = st.columns(3)
    
    with breakdown_cols[0]:
        st.metric("Price Anomalies", stats['price_anomalies'], help="Values significantly above/below historical average")
    
    with breakdown_cols[1]:
        st.metric("Vendor Dominance", stats['vendor_dominance'], help="Single vendor winning disproportionate share")
    
    with breakdown_cols[2]:
        st.metric("Low Competition", stats['low_competition'], help="Contracts with fewer than expected bidders")
    
    # === STEP 4: DETAILED FINDINGS ===
    st.markdown("""
    <div class="section-header">Step 4: Flagged Tenders Requiring Review</div>
    <div class="section-description">
    These tenders exhibit unusual statistical patterns compared to historical benchmarks.
    </div>
    """, unsafe_allow_html=True)
    
    if len(flagged) == 0:
        st.info("✓ No tenders were flagged based on the selected criteria.")
    else:
        # Prepare display
        display_columns = [
            'vendor_name',
            'inflation_adjusted_value',
            'contract_date',
            'department',
            'is_price_anomaly',
            'is_vendor_dominance',
            'is_low_competition'
        ]
        
        available_cols = [col for col in display_columns if col in flagged.columns]
        display_df = flagged[available_cols].copy()
        
        # Format values
        if 'inflation_adjusted_value' in display_df.columns:
            display_df['inflation_adjusted_value'] = display_df['inflation_adjusted_value'].apply(
                lambda x: f"₹{x/1_00_000:.2f}L" if x >= 1_00_000 else f"₹{x/1000:.0f}K"
            )
        
        if 'contract_date' in display_df.columns:
            display_df['contract_date'] = pd.to_datetime(display_df['contract_date']).dt.strftime('%Y-%m-%d')
        
        display_df = display_df.rename(columns={
            'vendor_name': 'Vendor',
            'inflation_adjusted_value': 'Contract Value',
            'contract_date': 'Date',
            'department': 'Department',
            'is_price_anomaly': 'Price Anomaly',
            'is_vendor_dominance': 'Vendor Dominance',
            'is_low_competition': 'Low Competition'
        })
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Detailed view
        st.markdown("**Detailed Explanations:**")
        
        for idx, row in flagged.iterrows():
            vendor_name = row.get('vendor_name', 'Unknown Vendor')
            value = row.get('inflation_adjusted_value', 0)
            value_str = f"₹{value/1_00_000:.2f}L" if value >= 1_00_000 else f"₹{value/1000:.0f}K"
            
            with st.expander(f"📌 {vendor_name} — {value_str}"):
                context = {
                    'median_value': stats['median_value'],
                    'mean_value': stats['mean_value'],
                    'total_contracts': stats['total_tenders']
                }
                explanation = generate_comprehensive_explanation(row, context)
                st.markdown(f"**Analysis:** {explanation}")
                
                # Key metrics
                metrics_cols = st.columns(3)
                with metrics_cols[0]:
                    if 'z_score' in row and pd.notna(row['z_score']):
                        st.metric("Z-Score", f"{row['z_score']:.2f}", help="Deviation from average (σ)")
                with metrics_cols[1]:
                    if 'ratio_to_median' in row and pd.notna(row['ratio_to_median']):
                        st.metric("Ratio to Median", f"{row['ratio_to_median']:.2f}×", help="Multiplier of median price")
                with metrics_cols[2]:
                    if 'vendor_contract_count' in row and pd.notna(row['vendor_contract_count']):
                        st.metric("Vendor Contracts", f"{int(row['vendor_contract_count'])}", help="Total contracts by vendor")
    
    # === STEP 5: CHARTS & TRENDS ===
    st.markdown("""
    <div class="section-header">Step 5: Charts & Trends</div>
    """, unsafe_allow_html=True)
    
    # Chart 1: Price Distribution
    st.markdown("**Contract Value Distribution**")
    st.markdown("Distribution of inflation-adjusted contract values. Helps identify outliers and common pricing ranges.")
    
    if 'inflation_adjusted_value' in df.columns:
        fig_price = px.histogram(
            df,
            x='inflation_adjusted_value',
            nbins=50,
            title=None,
            labels={'inflation_adjusted_value': 'Contract Value (₹)', 'count': 'Count'},
            color_discrete_sequence=['#0f172a']
        )
        fig_price.update_layout(
            template='plotly_white',
            font=dict(family="Arial, sans-serif", size=10),
            height=400,
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=40)
        )
        st.plotly_chart(fig_price, use_container_width=True)
    
    st.divider()
    
    # Chart 2: Vendor Dominance
    st.markdown("**Top Vendors by Contract Count**")
    st.markdown("Shows vendor concentration in the market. High concentration may reduce competition.")
    
    if 'vendor_contract_count' in df.columns:
        top_vendors = df.groupby('vendor_name')['vendor_contract_count'].first().nlargest(10)
        
        fig_vendors = px.bar(
            x=top_vendors.values,
            y=top_vendors.index,
            orientation='h',
            title=None,
            labels={'x': 'Number of Contracts', 'y': ''},
            color_discrete_sequence=['#0f172a']
        )
        fig_vendors.update_layout(
            template='plotly_white',
            font=dict(family="Arial, sans-serif", size=10),
            height=350,
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=200, r=40, t=20, b=40)
        )
        st.plotly_chart(fig_vendors, use_container_width=True)
    
    st.divider()
    
    # Chart 3: Competition Analysis
    st.markdown("**Contract Value by Competition Level**")
    st.markdown("Compares contract values across different levels of competitive bidding.")
    
    if 'num_bidders' in df.columns and df['num_bidders'].notna().any():
        competition_df = df[df['num_bidders'].notna()].copy()
        
        # Create competition category if it doesn't exist
        if 'competition_category' not in competition_df.columns:
            def categorize_competition(bidders):
                if bidders <= 1:
                    return 'Single Bidder'
                elif bidders <= 3:
                    return 'Low (2-3)'
                elif bidders <= 5:
                    return 'Moderate (4-5)'
                else:
                    return 'High (6+)'
            
            competition_df['competition_category'] = competition_df['num_bidders'].apply(categorize_competition)
        
        fig_competition = px.box(
            competition_df,
            x='competition_category',
            y='inflation_adjusted_value',
            title=None,
            labels={'inflation_adjusted_value': 'Contract Value (₹)', 'competition_category': 'Competition Level'},
            color_discrete_sequence=['#0f172a']
        )
        fig_competition.update_layout(
            template='plotly_white',
            font=dict(family="Arial, sans-serif", size=10),
            height=400,
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=40)
        )
        st.plotly_chart(fig_competition, use_container_width=True)
    
    # === STEP 6: EXPORT RESULTS ===
    st.markdown("""
    <div class="section-header">Step 6: Export & Reporting</div>
    <div class="section-description">
    Download your analysis results for further review or reporting.
    </div>
    """, unsafe_allow_html=True)
    
    export_cols = st.columns(2)
    
    with export_cols[0]:
        # CSV export
        csv = flagged.to_csv(index=False) if len(flagged) > 0 else df.to_csv(index=False)
        st.download_button(
            label="📥 Download Flagged Tenders (CSV)",
            data=csv,
            file_name=f"anviksha_flagged_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with export_cols[1]:
        # Summary report
        report = generate_summary_report(stats, flagged)
        st.download_button(
            label="📄 Download Summary Report (TXT)",
            data=report,
            file_name=f"anviksha_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )


def generate_summary_report(stats: dict, flagged: pd.DataFrame) -> str:
    """Generate a plain text summary report."""
    report_lines = [
        "=" * 70,
        "ANVIKSHA — PROCUREMENT ANALYSIS REPORT",
        "=" * 70,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "SUMMARY STATISTICS",
        "-" * 70,
        f"Total Tenders Analyzed:     {stats['total_tenders']:,}",
        f"Flagged Tenders:            {stats['flagged_tenders']:,} ({stats['flagged_tenders']/stats['total_tenders']*100:.1f}%)",
        f"Median Contract Value:      ₹{stats['median_value']/1_00_000:.2f} lakh",
        f"Unique Vendors:             {stats['unique_vendors']:,}",
        "",
        "ANOMALY BREAKDOWN",
        "-" * 70,
        f"Price Anomalies:            {stats['price_anomalies']}",
        f"Vendor Dominance:           {stats['vendor_dominance']}",
        f"Low Competition:            {stats['low_competition']}",
        "",
    ]
    
    if len(flagged) > 0:
        report_lines.extend([
            "FLAGGED TENDERS",
            "-" * 70,
        ])
        
        for idx, row in flagged.iterrows():
            report_lines.append(f"\n[Tender #{idx}]")
            report_lines.append(f"  Vendor:        {row.get('vendor_name', 'Unknown')}")
            report_lines.append(f"  Value:         ₹{row.get('inflation_adjusted_value', 0)/1_00_000:.2f} lakh")
            report_lines.append(f"  Date:          {row.get('contract_date', 'Unknown')}")
            
            flags = []
            if row.get('is_price_anomaly'):
                flags.append("Price Anomaly")
            if row.get('is_vendor_dominance'):
                flags.append("Vendor Dominance")
            if row.get('is_low_competition'):
                flags.append("Low Competition")
            
            report_lines.append(f"  Signals:       {', '.join(flags) if flags else 'None'}")
    
    report_lines.extend([
        "",
        "=" * 70,
        "NOTES",
        "-" * 70,
        "This report identifies statistical anomalies in procurement data.",
        "It is intended to support research and transparency initiatives.",
        "Further investigation may be warranted for flagged items.",
        "=" * 70,
    ])
    
    return "\n".join(report_lines)


if __name__ == "__main__":
    main()
