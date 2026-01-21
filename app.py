"""
Anviksha - Main Streamlit Application

Analytical Examination of Public Procurement Data
A research-focused tool for analyzing road construction tenders in West Bengal, India.
"""

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, HTMLResponse
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import traceback
from flask import Flask, send_from_directory

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Disable caching completely for development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.after_request
def add_no_cache_headers(response):
    """Add headers to disable caching on all responses"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Override static file serving to prevent caching
@app.route('/static/<path:filename>')
def custom_static(filename):
    response = send_from_directory(app.static_folder, filename)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

# Global variable to cache data
_cached_data = None

def load_data():
    """Load and cache the dataset"""
    global _cached_data
    
    if _cached_data is not None:
        return _cached_data.copy()
    
    try:
        df = pd.read_csv('sample_data/west_bengal_road_tenders_sample.csv')
        
        # Clean data
        df['Award_Year'] = pd.to_numeric(df['Award_Year'], errors='coerce').dropna().astype(int)
        df['Project_Length_km'] = pd.to_numeric(df['Project_Length_km'], errors='coerce').fillna(0)
        df['Tender_Value_Adjusted_Rs'] = pd.to_numeric(df['Tender_Value_Adjusted_Rs'], errors='coerce').fillna(0)
        
        for col in ['District', 'Department', 'Vendor_Name', 'Road_Type', 'Project_Name']:
            if col in df.columns:
                df[col] = df[col].fillna('Unknown').astype(str)
        
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
        print(f"📍 Districts: {df['District'].nunique()}")
        
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
    avg_cost_per_km = (total_spending / total_length) if total_length > 0 else 0
    districts_count = int(df['District'].nunique())
    
    years = sorted(df['Award_Year'].unique())
    time_range = f"{years[0]}-{years[-1]}" if len(years) > 1 else str(years[0]) if years else 'N/A'
    
    return {
        'total_spending': total_spending,
        'total_projects': total_projects,
        'avg_cost_per_km': avg_cost_per_km,
        'districts_count': districts_count,
        'time_range': time_range
    }

def detect_patterns(df):
    """Detect patterns"""
    observations = []
    
    if df.empty or len(df) < 10:
        return observations
    
    try:
        threshold = df['Tender_Value_Adjusted_Rs'].quantile(0.90)
        high_cost = df[df['Tender_Value_Adjusted_Rs'] > threshold]
        
        if len(high_cost) > 0:
            observations.append({
                'type': 'high_cost',
                'title': 'High-Value Projects Detected',
                'description': f'{len(high_cost)} project(s) exceed 90th percentile (₹{threshold/10000000:.2f} Cr).',
                'confidence': 'High',
                'confidence_reason': '90th percentile threshold',
                'does_not_imply': 'Inefficiency. May reflect project complexity.'
            })
    except:
        pass
    
    return observations

def generate_year_chart(df):
    """Generate year chart"""
    if df.empty:
        return ""
    
    try:
        yearly = df.groupby('Award_Year')['Tender_Value_Adjusted_Rs'].sum().sort_index()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(yearly.index, yearly.values / 10000000, marker='o', linewidth=2, color='#3b82f6')
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Spending (₹ Crore)', fontsize=12)
        ax.set_title('Year-wise Spending', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return img
    except:
        return ""

def generate_district_chart(df):
    """Generate district chart"""
    if df.empty:
        return ""
    
    try:
        district = df.groupby('District')['Tender_Value_Adjusted_Rs'].sum().sort_values(ascending=False).head(10)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(district.index, district.values / 10000000, color='#10b981')
        ax.set_xlabel('Spending (₹ Crore)', fontsize=12)
        ax.set_ylabel('District', fontsize=12)
        ax.set_title('Top Districts', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return img
    except:
        return ""

def generate_vendor_chart(df):
    """Generate vendor chart"""
    if df.empty or 'Vendor_Name' not in df.columns:
        return ""
    
    try:
        vendor = df.groupby('Vendor_Name')['Tender_Value_Adjusted_Rs'].sum().sort_values(ascending=False).head(5)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(vendor.index, vendor.values / 10000000, color='#f59e0b')
        ax.set_xlabel('Contract Value (₹ Crore)', fontsize=12)
        ax.set_ylabel('Vendor', fontsize=12)
        ax.set_title('Top Vendors', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return img
    except:
        return ""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    print("\n" + "="*50)
    print("HOME PAGE REQUEST")
    print("="*50)
    
    df = load_data()
    
    if df.empty:
        print("❌ NO DATA!")
        districts = ['all']
        departments = ['all']
        years = []
    else:
        districts = ['all'] + sorted(df['District'].unique().tolist())
        departments = ['all'] + sorted(df['Department'].unique().tolist())
        years = sorted(df['Award_Year'].unique().tolist(), reverse=True)
        
        print(f"✅ Data loaded: {len(df)} rows")
        print(f"📅 Years: {years}")
        print(f"📍 Districts: {len(districts)-1}")
        print(f"🏢 Departments: {len(departments)-1}")
    
    stats = calculate_stats(df)
    observations = detect_patterns(df)
    
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
    
    table_data = df.head(100).to_dict('records') if not df.empty else []
    
    print(f"📊 Table rows: {len(table_data)}")
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
    df = load_data()
    if df.empty:
        return StreamingResponse(iter(["No data\n"]), media_type="text/csv")
    
    summary = df.groupby(['Award_Year', 'District', 'Department']).agg({
        'Tender_Value_Adjusted_Rs': 'sum',
        'Project_Length_km': 'sum'
    }).reset_index()
    
    stream = io.StringIO()
    summary.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=summary.csv"
    return response

@app.get("/export/detailed")
async def export_detailed():
    df = load_data()
    if df.empty:
        return StreamingResponse(iter(["No data\n"]), media_type="text/csv")
    
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=detailed.csv"
    return response

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Anviksha server...")
    print("📂 Looking for data at: sample_data/west_bengal_road_tenders_sample.csv")
    print("🌐 Open browser at: http://localhost:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
