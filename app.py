"""
Anviksha - Main Streamlit Application

Analytical Examination of Public Procurement Data
A research-focused tool for analyzing road construction tenders in West Bengal, India.
"""

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import traceback
import time

# Custom middleware to disable caching
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        print(f"🔄 Response headers set for: {request.url.path}")
        return response

app = FastAPI()

# Add no-cache middleware FIRST
app.add_middleware(NoCacheMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Add auto-reload for templates
templates.env.auto_reload = True

# Global variable to cache data
_cached_data = None

def load_data():
    """Load and cache the dataset"""
    global _cached_data
    
    if _cached_data is not None:
        return _cached_data.copy()
    
    try:
        df = pd.read_csv('sample_data/west_bengal_road_tenders_sample.csv')
        
        print(f"📂 Raw CSV loaded: {len(df)} rows")
        print(f"📋 Columns: {df.columns.tolist()}")
        
        # Clean data
        df['Award_Year'] = pd.to_numeric(df['Award_Year'], errors='coerce')
        df = df.dropna(subset=['Award_Year'])
        df['Award_Year'] = df['Award_Year'].astype(int)
        
        df['Project_Length_km'] = pd.to_numeric(df['Project_Length_km'], errors='coerce').fillna(0)
        df['Tender_Value_Adjusted_Rs'] = pd.to_numeric(df['Tender_Value_Adjusted_Rs'], errors='coerce').fillna(0)
        
        for col in ['District', 'Department', 'Vendor_Name', 'Road_Type', 'Project_Name']:
            if col in df.columns:
                df[col] = df[col].fillna('Unknown').astype(str).str.strip()
        
        if 'Bidders_Count' in df.columns:
            df['Bidders_Count'] = pd.to_numeric(df['Bidders_Count'], errors='coerce').fillna(0).astype(int)
        else:
            df['Bidders_Count'] = 0
        
        # Remove invalid data
        df = df[df['Award_Year'] > 2000]
        df = df[df['Tender_Value_Adjusted_Rs'] > 0]
        
        _cached_data = df.copy()
        
        print(f"✅ DATA LOADED: {len(df)} rows")
        print(f"📅 Years: {sorted(df['Award_Year'].unique())}")
        print(f"📍 Districts ({df['District'].nunique()}): {sorted(df['District'].unique())}")
        print(f"🏢 Departments ({df['Department'].nunique()}): {sorted(df['Department'].unique())}")
        
        return df.copy()
        
    except Exception as e:
        print(f"❌ ERROR loading data: {e}")
        traceback.print_exc()
        return pd.DataFrame()

def calculate_stats(df):
    """Calculate statistics"""
    if df.empty:
        return {
            'total_spending': 0,
            'total_projects': 0,
            'avg_cost_per_km': 0,
            'districts_count': 0,
            'time_range': 'N/A'
        }
    
    total_spending = float(df['Tender_Value_Adjusted_Rs'].sum())
    total_projects = len(df)
    total_length = float(df['Project_Length_km'].sum())
    
    # Calculate avg cost per km (in Rs, not lakhs)
    avg_cost_per_km = (total_spending / total_length) if total_length > 0 else 0
    
    districts_count = int(df['District'].nunique())
    
    years = sorted(df['Award_Year'].unique())
    time_range = f"{years[0]}-{years[-1]}" if len(years) > 1 else str(years[0]) if years else 'N/A'
    
    return {
        'total_spending': total_spending,
        'total_projects': total_projects,
        'avg_cost_per_km': avg_cost_per_km,  # This is now in rupees
        'districts_count': districts_count,
        'time_range': time_range
    }

def detect_patterns(df):
    """Detect statistical patterns in the data"""
    observations = []
    
    if df.empty or len(df) < 10:
        return observations
    
    try:
        # 1. HIGH-COST OUTLIERS (using IQR method)
        q3 = df['Tender_Value_Adjusted_Rs'].quantile(0.75)
        q1 = df['Tender_Value_Adjusted_Rs'].quantile(0.25)
        iqr = q3 - q1
        outlier_threshold = q3 + 1.5 * iqr
        median_value = df['Tender_Value_Adjusted_Rs'].median()
        
        high_cost = df[df['Tender_Value_Adjusted_Rs'] > outlier_threshold]
        
        for _, row in high_cost.iterrows():
            ratio = row['Tender_Value_Adjusted_Rs'] / median_value if median_value > 0 else 1
            percentile = (df['Tender_Value_Adjusted_Rs'] <= row['Tender_Value_Adjusted_Rs']).sum() / len(df) * 100
            
            observations.append({
                'type': 'high_cost',
                'title': 'High-Value Project Detected',
                'description': (
                    f"Project '{row['Project_Name']}' in {row['District']} has an inflation-adjusted value of "
                    f"₹{row['Tender_Value_Adjusted_Rs']/10000000:.2f} Cr, which is {ratio:.1f}× the median value "
                    f"(₹{median_value/10000000:.2f} Cr). This places it in the {percentile:.0f}th percentile."
                ),
                'confidence': 'High',
                'confidence_reason': 'Statistical deviation detected via IQR method (>Q3 + 1.5×IQR)',
                'does_not_imply': 'Inefficiency or wrongdoing. High values may reflect project complexity, scope, terrain difficulty, or specialized requirements.'
            })
        
        # 2. LOW COMPETITION + HIGH VALUE
        if 'Bidders_Count' in df.columns:
            low_bidder_threshold = 3
            high_value_threshold = df['Tender_Value_Adjusted_Rs'].quantile(0.75)
            median_bidders = df['Bidders_Count'].median()
            
            low_competition = df[
                (df['Bidders_Count'] <= low_bidder_threshold) & 
                (df['Tender_Value_Adjusted_Rs'] > high_value_threshold)
            ]
            
            for _, row in low_competition.iterrows():
                observations.append({
                    'type': 'low_competition',
                    'title': 'Limited Bidder Participation Observed',
                    'description': (
                        f"Project '{row['Project_Name']}' received {int(row['Bidders_Count'])} bidder(s) "
                        f"(compared to a median of {median_bidders:.0f} bidders across all projects). "
                        f"The contract value is ₹{row['Tender_Value_Adjusted_Rs']/10000000:.2f} Cr, which is in the top quartile."
                    ),
                    'confidence': 'Medium',
                    'confidence_reason': 'Rule-based detection: bidders ≤3 AND value ≥75th percentile',
                    'does_not_imply': 'Restricted bidding or improper procurement. May indicate specialized requirements, remote location, or limited vendor availability in the district.'
                })
        
        # 3. VENDOR CONCENTRATION
        vendor_counts = df.groupby('Vendor_Name').size()
        total_projects = len(df)
        high_concentration_vendors = vendor_counts[vendor_counts / total_projects > 0.2]
        
        for vendor_name, count in high_concentration_vendors.items():
            vendor_total = df[df['Vendor_Name'] == vendor_name]['Tender_Value_Adjusted_Rs'].sum()
            observations.append({
                'type': 'vendor_concentration',
                'title': 'Vendor Market Share Pattern',
                'description': (
                    f"{vendor_name} has been awarded {count} project(s) ({count/total_projects*100:.1f}% of total) "
                    f"with a combined value of ₹{vendor_total/10000000:.2f} Cr in the current selection."
                ),
                'confidence': 'Medium',
                'confidence_reason': 'Descriptive market share calculation (>20% of projects)',
                'does_not_imply': 'Favoritism or irregularity. High share may reflect vendor capability, experience, competitive pricing, or limited competition in specialized categories.'
            })
    
    except Exception as e:
        print(f"Error in detect_patterns: {e}")
        import traceback
        traceback.print_exc()
    
    return observations

def generate_year_chart(df):
    """Generate year-wise spending chart"""
    if df.empty:
        return ""
    
    try:
        yearly = df.groupby('Award_Year')['Tender_Value_Adjusted_Rs'].sum().sort_index()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(yearly.index, yearly.values / 10000000, marker='o', linewidth=2, color='#3b82f6')
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Spending (₹ Crore)', fontsize=12)
        ax.set_title('Year-wise Spending Trend', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return img
    except Exception as e:
        print(f"Error generating year chart: {e}")
        return ""

def generate_district_chart(df):
    """Generate district-wise spending chart"""
    if df.empty:
        return ""
    
    try:
        district = df.groupby('District')['Tender_Value_Adjusted_Rs'].sum().sort_values(ascending=False).head(10)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(district.index, district.values / 10000000, color='#10b981')
        ax.set_xlabel('Spending (₹ Crore)', fontsize=12, fontweight='bold')
        ax.set_ylabel('District', fontsize=12, fontweight='bold')
        ax.set_title('Top 10 Districts by Spending', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return img
    except Exception as e:
        print(f"Error generating district chart: {e}")
        return ""

def generate_vendor_chart(df):
    """Generate vendor-wise spending chart"""
    if df.empty or 'Vendor_Name' not in df.columns:
        return ""
    
    try:
        vendor = df.groupby('Vendor_Name')['Tender_Value_Adjusted_Rs'].sum().sort_values(ascending=False).head(5)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(vendor.index, vendor.values / 10000000, color='#f59e0b')
        ax.set_xlabel('Contract Value (₹ Crore)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Vendor', fontsize=12, fontweight='bold')
        ax.set_title('Top 5 Vendors by Contract Value', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return img
    except Exception as e:
        print(f"Error generating vendor chart: {e}")
        return ""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    print("\n" + "="*50)
    print(f"HOME PAGE REQUEST at {time.strftime('%H:%M:%S')}")
    print("="*50)
    
    # Clear cache to force reload
    global _cached_data
    _cached_data = None
    
    df = load_data()
    
    if df.empty:
        print("❌ NO DATA!")
        districts = ['all']
        departments = ['all']
        years = []
    else:
        # Get unique districts and departments
        unique_districts = sorted(df['District'].unique().tolist())
        unique_departments = sorted(df['Department'].unique().tolist())
        
        districts = ['all'] + unique_districts
        departments = ['all'] + unique_departments
        years = sorted(df['Award_Year'].unique().tolist(), reverse=True)
        
        print(f"✅ Data loaded: {len(df)} rows")
        print(f"📅 Years ({len(years)}): {years}")
        print(f"📍 Districts ({len(unique_districts)}): {unique_districts}")
        print(f"🏢 Departments ({len(unique_departments)}): {unique_departments}")
    
    stats = calculate_stats(df)
    observations = detect_patterns(df)
    
    print(f"🔍 Observations detected: {len(observations)}")
    for obs in observations:
        print(f"  - {obs['type']}: {obs['title']}")
    
    year_chart = generate_year_chart(df)
    district_chart = generate_district_chart(df)
    vendor_chart = generate_vendor_chart(df)
    
    # Aggregated data
    year_spending = []
    district_spending = []
    vendor_stats = []
    
    if not df.empty:
        ys = df.groupby('Award_Year')['Tender_Value_Adjusted_Rs'].sum().reset_index()
        year_spending = ys.rename(columns={'Tender_Value_Adjusted_Rs': 'Total_Spending'}).to_dict('records')
        
        ds = df.groupby('District')['Tender_Value_Adjusted_Rs'].sum().reset_index()
        district_spending = ds.rename(columns={'Tender_Value_Adjusted_Rs': 'Total_Spending'}).sort_values('Total_Spending', ascending=False).to_dict('records')
        
        if 'Vendor_Name' in df.columns:
            vs = df.groupby('Vendor_Name')['Tender_Value_Adjusted_Rs'].sum().reset_index().nlargest(5, 'Tender_Value_Adjusted_Rs')
            vendor_stats = vs.rename(columns={'Tender_Value_Adjusted_Rs': 'Total_Value'}).to_dict('records')
    
    # FIX: Convert DataFrame to list of dicts
    table_data = df.head(100).to_dict('records') if not df.empty else []
    
    print(f"📊 Table rows: {len(table_data)}")
    print(f"🔄 Template will reload: templates/index.html")
    print("="*50 + "\n")
    
    context = {
        "request": request,
        "districts": districts,
        "departments": departments,
        "years": years,
        "stats": stats,
        "observations": observations,
        "year_chart": year_chart,
        "district_chart": district_chart,
        "vendor_chart": vendor_chart,
        "table_data": table_data,
        "year_spending": year_spending,
        "district_spending": district_spending,
        "vendor_stats": vendor_stats,
        "selected_filters": {'district': 'all', 'department': 'all', 'year': 'all'}
    }
    
    return templates.TemplateResponse("index.html", context)

@app.post("/filter", response_class=HTMLResponse)
async def filter_data(request: Request, district: str = Form(...), department: str = Form(...), year: str = Form("all")):
    """Filter endpoint"""
    print("\n" + "="*50)
    print(f"FILTER: District={district}, Dept={department}, Year={year}")
    print("="*50)
    
    df = load_data()
    print(f"Initial: {len(df)} rows")
    
    if district != "all":
        df = df[df['District'] == district]
        print(f"After district: {len(df)} rows")
    
    if department != "all":
        df = df[df['Department'] == department]
        print(f"After dept: {len(df)} rows")
    
    if year != "all":
        df = df[df['Award_Year'] == int(year)]
        print(f"After year: {len(df)} rows")
    
    selected_filters = {'district': district, 'department': department, 'year': year}
    
    stats = calculate_stats(df)
    observations = detect_patterns(df)
    
    print(f"🔍 Filtered observations: {len(observations)}")
    
    year_chart = generate_year_chart(df)
    district_chart = generate_district_chart(df)
    vendor_chart = generate_vendor_chart(df)
    
    year_spending = []
    district_spending = []
    vendor_stats = []
    
    if not df.empty:
        ys = df.groupby('Award_Year')['Tender_Value_Adjusted_Rs'].sum().reset_index()
        year_spending = ys.rename(columns={'Tender_Value_Adjusted_Rs': 'Total_Spending'}).to_dict('records')
        
        ds = df.groupby('District')['Tender_Value_Adjusted_Rs'].sum().reset_index()
        district_spending = ds.rename(columns={'Tender_Value_Adjusted_Rs': 'Total_Spending'}).sort_values('Total_Spending', ascending=False).to_dict('records')
        
        if 'Vendor_Name' in df.columns:
            vs = df.groupby('Vendor_Name')['Tender_Value_Adjusted_Rs'].sum().reset_index().nlargest(5, 'Tender_Value_Adjusted_Rs')
            vendor_stats = vs.rename(columns={'Tender_Value_Adjusted_Rs': 'Total_Value'}).to_dict('records')
    
    # FIX: Convert DataFrame to list of dicts
    table_data = df.head(100).to_dict('records') if not df.empty else []
    
    print(f"✅ Returning {len(table_data)} rows")
    print("="*50 + "\n")
    
    context = {
        "request": request,
        "stats": stats,
        "observations": observations,
        "selected_filters": selected_filters,
        "year_chart": year_chart,
        "district_chart": district_chart,
        "vendor_chart": vendor_chart,
        "table_data": table_data,
        "year_spending": year_spending,
        "district_spending": district_spending,
        "vendor_stats": vendor_stats
    }
    
    return templates.TemplateResponse("partials/results.html", context)

@app.get("/export/summary")
async def export_summary():
    """Export aggregated summary data as CSV"""
    try:
        df = load_data()
        if df.empty:
            # Return empty CSV with headers
            headers = "District,Department,Award_Year,Total_Projects,Total_Spending_Cr,Avg_Project_Value_Cr,Total_Length_Km\n"
            return StreamingResponse(
                iter([headers]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=anviksha_summary_export.csv"}
            )
        
        # Create aggregated summary
        summary = df.groupby(['District', 'Department', 'Award_Year']).agg({
            'Tender_ID': 'count',
            'Tender_Value_Adjusted_Rs': ['sum', 'mean'],
            'Project_Length_km': 'sum'
        }).reset_index()
        
        # Flatten column names
        summary.columns = ['District', 'Department', 'Award_Year', 'Total_Projects', 
                          'Total_Spending_Rs', 'Avg_Project_Value_Rs', 'Total_Length_Km']
        
        # Convert to crores for readability
        summary['Total_Spending_Cr'] = (summary['Total_Spending_Rs'] / 10000000).round(2)
        summary['Avg_Project_Value_Cr'] = (summary['Avg_Project_Value_Rs'] / 10000000).round(2)
        
        # Drop rupee columns, keep crore columns
        summary = summary[['District', 'Department', 'Award_Year', 'Total_Projects', 
                          'Total_Spending_Cr', 'Avg_Project_Value_Cr', 'Total_Length_Km']]
        
        # Sort by year and district
        summary = summary.sort_values(['Award_Year', 'District', 'Department'])
        
        # Convert to CSV
        stream = io.StringIO()
        summary.to_csv(stream, index=False)
        stream.seek(0)
        
        return StreamingResponse(
            iter([stream.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=anviksha_summary_export.csv"}
        )
    
    except Exception as e:
        print(f"Error in export_summary: {e}")
        import traceback
        traceback.print_exc()
        return StreamingResponse(
            iter([f"Error generating export: {str(e)}\n"]),
            media_type="text/plain"
        )

@app.get("/export/detailed")
async def export_detailed():
    """Export complete detailed data as CSV"""
    try:
        df = load_data()
        if df.empty:
            # Return empty CSV with headers
            headers = "Tender_ID,Award_Year,District,Department,Project_Name,Vendor_Name,Project_Length_km,Tender_Value_Cr,Bidders_Count,Road_Type\n"
            return StreamingResponse(
                iter([headers]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=anviksha_detailed_export.csv"}
            )
        
        # Create export dataframe with all columns
        export_df = df.copy()
        
        # Add computed columns
        export_df['Tender_Value_Cr'] = (export_df['Tender_Value_Adjusted_Rs'] / 10000000).round(2)
        export_df['Cost_Per_Km_Lakh'] = ((export_df['Tender_Value_Adjusted_Rs'] / export_df['Project_Length_km']) / 100000).round(2)
        
        # Select and order columns for export
        export_columns = [
            'Tender_ID', 'Award_Year', 'District', 'Department', 
            'Project_Name', 'Vendor_Name', 'Project_Length_km', 
            'Tender_Value_Cr', 'Cost_Per_Km_Lakh', 'Bidders_Count', 'Road_Type'
        ]
        
        export_df = export_df[export_columns]
        
        # Sort by year and district
        export_df = export_df.sort_values(['Award_Year', 'District'])
        
        # Convert to CSV
        stream = io.StringIO()
        export_df.to_csv(stream, index=False)
        stream.seek(0)
        
        return StreamingResponse(
            iter([stream.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=anviksha_detailed_export.csv"}
        )
    
    except Exception as e:
        print(f"Error in export_detailed: {e}")
        import traceback
        traceback.print_exc()
        return StreamingResponse(
            iter([f"Error generating export: {str(e)}\n"]),
            media_type="text/plain"
        )

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Anviksha server...")
    print("📂 Looking for data at: sample_data/west_bengal_road_tenders_sample.csv")
    print("🌐 Open browser at: http://localhost:8000")
    print("⚠️  CACHE DISABLED - Changes will appear immediately")
    print("🔄 AUTO-RELOAD ENABLED\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=True)
